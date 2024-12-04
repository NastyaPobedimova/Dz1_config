import os
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timedelta
import io
import configparser
import time
import platform
import sys

class ShellEmulator:
    def __init__(self, config_path):
        self.init(config_path)

    def init(self, config_path):

        try:
            self.config = self.load_config(config_path)
        except Exception as e:
            try:
                with open(config_path, "r", encoding='utf-8') as f:
                    self.config = toml.load(f)
            except Exception as toml_e:
                print(f"Ошибка при загрузке конфигурации: {str(e)}")
                print(f"Также не удалось загрузить как TOML: {str(toml_e)}")
                sys.exit(1)

        self.username = self.config["user"]["name"]
        self.computer_name = self.config["user"]["computer"]
        self.fs_zip_path = self.config["paths"]["vfs"]
        self.log_file = self.config["paths"]["log"]
        self.current_path = ["/"]  # Use a list to represent the path
        self.vfs = {}
        self.hist = []
        self.start = time.time()
        self.start_ = datetime.now()
        self.load_vfs()

    def load_config(self, config_path: str) -> dict:
        config = configparser.ConfigParser()
        config.read(config_path, encoding='utf-8')
        return {
            "user": {
                "name": config.get("user", "name"),
                "computer": config.get("user", "computer")
            },
            "paths": {
                "vfs": config.get("paths", "vfs"),
                "log": config.get("paths", "log")
            }
        }

    def load_vfs(self):
        self.vfs = {}  # Очищаем структуру перед загрузкой
        with zipfile.ZipFile(self.fs_zip_path, "r") as zip_ref:
            for file in zip_ref.namelist():
                if not file.endswith('/'):  # Пропускаем пустые директории
                    parts = [p for p in file.split('/') if p]
                    current = self.vfs
                    
                    # Создаем структуру директорий
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                        if isinstance(current, bytes):
                            # Если текущий уровень оказался файлом, создаем новый словарь
                            current = {}
                    
                    # Добавляем файл только если это не директория
                    if parts:
                        filename = parts[-1]
                        if not isinstance(current, bytes):
                            current[filename] = zip_ref.read(file)

    def _is_directory(self, path):
        """Проверяет, является ли путь директорией"""
        current = self.vfs
        for part in path[1:]:  # Пропускаем корневой слэш
            if part not in current:
                return False
            current = current[part]
            if not isinstance(current, dict):
                return False
        return True

    def _is_file(self, path):
        """Проверяет, является ли путь файлом"""
        current = self.vfs
        for part in path[1:-1]:  # Пропускаем корневой слэш и последний элемент
            if part not in current or not isinstance(current[part], dict):
                return False
            current = current[part]
        return path[-1] in current and isinstance(current[path[-1]], bytes)

    def prompt(self):
        path_str = "/".join(self.current_path[1:])  # Convert path list to string
        return f"{self.username}@{self.computer_name}:{path_str}$ "

    def execute(self, command):
        parts = command.split()
        if not parts:
            return

        cmd = parts[0]
        args = parts[1:]

        if command.startswith("cd "):
            self.cd(command[3:])
            self.hist.append(command)
        elif command.startswith("ls"):
            if len(command) == 2:
                self.ls()
            else:
                self.ls_args(command[3:])
            self.hist.append(command)
        elif command.startswith("exit"):
            self.exit_shell()
            self.hist.append(command)
        elif command.startswith("mv"):
            self.mv(args[0], args[1])
            self.hist.append(command)
        elif command.startswith("history"):
            self.history()
            self.hist.append(command)
        elif command.startswith("uname"):
            self.uname()
            self.hist.append(command)
        else:
            print(f"Неизвестная команда: '{cmd}'", file=sys.stderr)

    def history(self):
        for command in self.hist:
            print(command)

    def uname(self):
        system_info = platform.uname()
        result = f"{system_info.system} {system_info.node} {system_info.release}"
        print(result)
        return result

    def cd(self, path_parts):
        if not path_parts or (isinstance(path_parts, list) and not path_parts):
            self.current_path = ["/"]
            return None

        # If path_parts is a list, take the first element
        if isinstance(path_parts, list):
            path = path_parts[0]
        else:
            path = path_parts

        # Обработка пути '..'
        if path == "..":
            if len(self.current_path) > 1:  # Если мы не в корневом каталоге
                self.current_path.pop()
            return None

        # Обработка пути '.'
        if path == ".":
            return None

        # Разделяем путь на части
        if '/' in path:
            parts = [p for p in path.split('/') if p]
        else:
            parts = [path]

        # Если путь начинается с '/', это абсолютный путь
        if isinstance(path, str) and path.startswith('/'):
            new_path = ["/"]
        else:
            new_path = self.current_path.copy()

        # Обрабатываем каждую часть пути
        for part in parts:
            if part == "..":
                if len(new_path) > 1:  # Не выходим за пределы корневого каталога
                    new_path.pop()
                continue
            elif part == ".":
                continue
            else:
                temp_path = new_path + [part]
                if not self._is_directory(temp_path):
                    print(f"cd: {part}: Нет такой директории")
                    return None
                new_path.append(part)

        self.current_path = new_path
        return None

    def _path_exists(self, path):
        """Проверяет существование пути (может быть как файлом, так и директорией)"""
        return self._is_directory(path) or self._is_file(path)

    def ls(self):
        current_level = self.vfs
        # Переходим к текущей директории
        for part in self.current_path[1:]:
            if part not in current_level:
                return None
            current_level = current_level[part]
            if not isinstance(current_level, dict):
                return None

        # Собираем содержимое текущей директории
        result = []
        for item in current_level:
            if isinstance(current_level[item], dict):
                result.append(f"{item}/")  # Добавляем слэш к именам директорий
            else:
                result.append(item)
        
        # Выводим и возвращаем результат
        for item in result:
            print(item)
        return result

    def ls_args(self, path):
        #Реализация ls с аргументами (добавить позже)
        pass

    def mv(self, source, destination):
        try:
            with zipfile.ZipFile(self.fs_zip_path, 'r') as zip_ref:
                # Get list of all files in archive
                file_list = zip_ref.namelist()
                
                # Get current path
                current_dir = "/".join(self.current_path[1:])
                
                # Form source path - if not absolute, make it relative to current dir
                if source.startswith('/'):
                    search_path = source.lstrip('/')
                else:
                    search_path = f"{current_dir}/{source}" if current_dir else source
                search_path = search_path.rstrip('/')
                
                # Check if source exists
                if search_path not in file_list:
                    print(f"mv: cannot stat '{source}': No such file or directory")
                    return False

                # Form destination path
                if destination.startswith('/'):
                    dest_path = destination.lstrip('/')
                else:
                    dest_path = f"{current_dir}/{destination}" if current_dir else destination
                dest_path = dest_path.rstrip('/')

                # If destination is a directory, append source filename
                is_dir = any(f.startswith(dest_path + '/') for f in file_list) if dest_path else False
                if is_dir or destination.endswith('/'):
                    dest_path = f"{dest_path}/{os.path.basename(source)}"

                # Create temporary archive for updating files
                temp_zip_path = self.fs_zip_path + '.temp'
                with zipfile.ZipFile(temp_zip_path, 'w') as temp_zip:
                    # Copy all files except source
                    for item in file_list:
                        if item != search_path:
                            temp_zip.writestr(item, zip_ref.read(item))
                    
                    # Copy source to new location
                    temp_zip.writestr(dest_path, zip_ref.read(search_path))

            # Replace original archive with updated one
            os.replace(temp_zip_path, self.fs_zip_path)
            self.load_vfs()  # Reload virtual filesystem
            return True

        except Exception as e:
            print(f"mv: error while moving file: {str(e)}")
            if os.path.exists(temp_zip_path):
                os.remove(temp_zip_path)
            return False

    def list_files(self):
        """Returns a list of all files in the virtual file system"""
        files = []
        def traverse(current_dict, current_path=""):
            for name, content in current_dict.items():
                full_path = f"{current_path}/{name}" if current_path else name
                if isinstance(content, dict):
                    traverse(content, full_path)
                else:
                    files.append(full_path)
        traverse(self.vfs)
        return files

    def exit_shell(self):
        print("Exiting...")
        exit()

    def run(self):
        while True:
            command = input(self.prompt())
            self.execute(command)
            if command.lower() == "exit":
                break


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python shell_emulator.py <config.toml>")
        sys.exit(1)

    config_path = sys.argv[1]
    print(config_path)
    shell =ShellEmulator(config_path)
    shell.run()

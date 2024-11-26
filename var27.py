import time
import os
import sys
import toml
import zipfile
from datetime import datetime
import platform

class ShellEmulator:
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.username = self.config["user"]["name"]
        self.computer_name = self.config["user"]["computer"]
        self.fs_zip_path = self.config["paths"]["vfs"]
        self.log_file = self.config["paths"]["log"]
        self.current_path = ["/"]
        self.vfs = {}
        self.hist = []
        self.start = time.time()
        self.start_ = datetime.now()
        self.load_vfs()

    def load_config(self, config_path: str) -> dict:
        with open(config_path, "r") as f:
            return toml.load(f)

    def load_vfs(self):
        try:
            with zipfile.ZipFile(self.fs_zip_path, "r") as zip_ref:
                for file_path in zip_ref.namelist():
                    parts = file_path.split('/')
                    current_level = self.vfs
                    for part in parts[:-1]:
                        if part: #Skip empty parts
                          current_level = current_level.setdefault(part, {})
                    if parts[-1]: #Skip empty filenames
                      current_level[parts[-1]] = zip_ref.read(file_path).decode('utf-8', errors='ignore')
        except FileNotFoundError:
            print(f"Error: VFS file not found: {self.fs_zip_path}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Ошибка при загрузке VFS: {e}", file=sys.stderr)
            sys.exit(1)


    def prompt(self):
        return f"{self.username}@{self.computer_name}:{os.path.join(*self.current_path)}$ "

    def execute(self, command):
        parts = command.split()
        if not parts:
            return

        cmd = parts[0]
        args = parts[1:]

        commands = {
            "cd": self.cd,
            "ls": self.ls,
            "mv": self.mv,
            "history": self.history,
            "uname": self.uname,
            "exit": self.exit_shell,
        }

        if cmd in commands:
            try:
                if cmd == "ls":
                    if args:
                        self.ls_args(args)
                    else:
                        self.ls()
                elif cmd in ["uname", "history"]: #Обработка uname и history
                    commands[cmd]() #Вызов без аргументов
                else:
                    commands[cmd](args)
                self.hist.append(command)
            except (ValueError, FileNotFoundError, KeyError, TypeError) as e:
                print(f"Ошибка: {e}", file=sys.stderr)
            except Exception as e:
                print(f"Произошла непредвиденная ошибка: {e}", file=sys.stderr)
        else:
            print(f"Неизвестная команда: '{cmd}'", file=sys.stderr)
    
    def history(self):
        for command in self.hist:
            print(command)

    def uname(self):
        system_info = platform.uname()
        print(f"{system_info.system} {system_info.node} {system_info.release}")

    def cd(self, args):
        if not args:
            self.current_path = ["/"]
            return

        new_path = self.current_path[:]
        for arg in args:
            if arg == "..":
                if len(new_path) > 1:
                    new_path.pop()
            else:
                new_path.append(arg)

        current_level = self.vfs
        for part in new_path[1:]:
            if part in current_level:
                current_level = current_level[part]
            else:
                print(f"Директория не найдена: {os.path.join(*args)}", file=sys.stderr)
                return

        self.current_path = new_path

    def ls(self):
        current_level = self.vfs
        for part in self.current_path[1:]:
            if part in current_level:
                current_level = current_level[part]
            else:
                print("Invalid current path!", file=sys.stderr)
                return

        for item in current_level:
            print(item)

    def mv(self, args):
        if len(args) != 2:
            print("Использование: mv <исходный_файл> <целевой_файл>", file=sys.stderr)
            return

        source_path = os.path.join(*self.current_path, args[0])
        dest_path = os.path.join(*self.current_path, args[1])

        source_parts = source_path.split('/')
        dest_parts = dest_path.split('/')

        source_level = self.vfs
        dest_level = self.vfs

        try:
            for part in source_parts[1:-1]:
                source_level = source_level[part]
            for part in dest_parts[1:-1]:
                dest_level = dest_level.setdefault(part, {})

            if source_parts[-1] in source_level:
                if dest_parts[-1] in dest_level:
                    print("Файл с таким именем уже существует.", file=sys.stderr)
                else:
                    dest_level[dest_parts[-1]] = source_level[source_parts[-1]]
                    del source_level[source_parts[-1]]
                    print(f"Перемещено: {source_path} -> {dest_path}")
            else:
                print(f"Исходный файл не найден: {source_path}", file=sys.stderr)

        except (KeyError, TypeError) as e:
            print(f"Ошибка перемещения файла: {e}", file=sys.stderr)


    def exit_shell(self):
        end = time.time()
        end_ = datetime.now()
        total_time = end - self.start
        print(f"Сессия длилась {total_time:.2f} секунд")
        exit()

    def ls_args(self, args):
        if self.cd(args) == -1:
            return
        self.ls()
        if len(self.current_path) > 1:
            self.cd([".."])

    def run(self):
        while True:
            command = input(self.prompt())
            self.execute(command)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python shell_emulator.py <config.toml>", file=sys.stderr)
        sys.exit(1)
    config_path = sys.argv[1]
    shell = ShellEmulator(config_path)
    shell.run()
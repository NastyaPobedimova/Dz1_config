from main import Terminal
from main import Application
from types import NoneType
import pytest
from zipfile import ZipFile
import platform
import io

@pytest.fixture
def terminal():
    name = "MyComputer"
    fs_path = "vfs.zip"
    t = Terminal(name, fs_path, ZipFile(fs_path, "a"))
    #Создание файлов для тестов
    with t.filesystem as zf:
        zf.writestr("test.txt", "test content")
        zf.writestr("Yesenin_s_dir_1/file1.txt", "content1")
    return t

def test_init_1(terminal):
    assert terminal.application is None

def test_init_2(terminal):
    assert terminal.filesystem is not None

def test_init_3(terminal):
    assert terminal.log_path is not None

def test_link(terminal):
    terminal.link(Application(terminal))
    assert terminal.application is not None

def test_cd_1(terminal, capfd):
    terminal.cd([])
    out, err = capfd.readouterr()
    assert terminal.current_path == "/"
    assert err == ""

def test_cd_2(terminal, capfd):
    terminal.cd(["Yesenin_s_dir_1/.."])
    out, err = capfd.readouterr()
    assert terminal.current_path == "/"
    assert err == ""

def test_cd_3(terminal, capfd):
    terminal.cd(["Yesenin_s_dir_1"])
    out, err = capfd.readouterr()
    assert terminal.current_path == "/Yesenin_s_dir_1"
    assert err == ""

def test_ls_1(terminal, capfd):
    terminal.ls()
    out, err = capfd.readouterr()
    assert "test.txt" in out
    assert "Yesenin_s_dir_1" in out
    assert err == ""

def test_ls_2(terminal, capfd):
    terminal.cd(["Yesenin_s_dir_1"])
    terminal.ls()
    out, err = capfd.readouterr()
    assert "file1.txt" in out
    assert err == ""

def test_ls_3(terminal, capfd):
    terminal.cd(["nonexistent_dir"])
    terminal.ls()
    out, err = capfd.readouterr()
    assert "Директория не найдена" in err


def test_uname_1(terminal, capfd):
    terminal.uname()
    out, err = capfd.readouterr()
    system_info = platform.uname()
    expected = f"{system_info.system} {system_info.node} {system_info.release}"
    assert expected in out
    assert err == ""

def test_uname_2(terminal, capfd):
    terminal.uname()
    out, err = capfd.readouterr()
    assert err == ""


def test_uname_3(terminal, capfd):
    terminal.uname()
    out, err = capfd.readouterr()
    assert err == ""


def test_history_1(terminal, capfd):
    terminal.command_history = []
    terminal.execute("ls")
    terminal.execute("cd ..")
    terminal.history()
    out, err = capfd.readouterr()
    assert "ls" in out
    assert "cd .." in out
    assert err == ""

def test_history_2(terminal, capfd):
    terminal.command_history = ["cd /", "ls -l"]
    terminal.history()
    out, err = capfd.readouterr()
    assert "cd /" in out
    assert "ls -l" in out
    assert err == ""

def test_history_3(terminal, capfd):
    terminal.command_history = []
    terminal.history()
    out, err = capfd.readouterr()
    assert out == ""
    assert err == ""

def test_mv_1(terminal, capfd):
    terminal.mv(["test.txt", "new_test.txt"])
    out, err = capfd.readouterr()
    assert "Перемещено" in out
    assert "test.txt" not in terminal.filesystem.namelist()
    assert "new_test.txt" in terminal.filesystem.namelist()
    assert err == ""


def test_mv_2(terminal, capfd):
    terminal.mv(["nonexistent_file.txt", "another_file.txt"])
    out, err = capfd.readouterr()
    assert "Исходный файл не найден" in err
    assert err != ""

def test_mv_3(terminal, capfd):
    terminal.mv(["test.txt"])
    out, err = capfd.readouterr()
    assert "Неправильное использование команды mv" in err
    assert err != ""

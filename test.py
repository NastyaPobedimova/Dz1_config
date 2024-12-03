from main import ShellEmulator
import pytest
from zipfile import ZipFile
import platform
import warnings

# Игнорируем предупреждения о дубликатах в ZIP-файле
warnings.filterwarnings("ignore", category=UserWarning, module="zipfile")

@pytest.fixture
def shellEmulator():
    config_path = "config.toml"
    t = ShellEmulator(config_path)
    return t

def test_init_2(shellEmulator):
    assert shellEmulator.fs_zip_path is not None 

def test_init_3(shellEmulator):
    assert shellEmulator.log_file is not None

def test_cd_1(shellEmulator):
    assert shellEmulator.cd([]) == None

def test_cd_2(shellEmulator):
    assert shellEmulator.cd(["Yesenin_s_dir_1/.."]) == None

def test_cd_3(shellEmulator):
    shellEmulator.cd([])
    shellEmulator.cd(["Yesenin_s_dir_1"])
    assert "Yesenin_s_dir_1" in shellEmulator.current_path

def test_ls_1(shellEmulator):
    result = shellEmulator.ls()
    assert result is not None
    assert isinstance(result, list)

def test_ls_2(shellEmulator):
    shellEmulator.cd(["Yesenin_s_dir_1"])
    result = shellEmulator.ls()
    assert result is not None
    assert isinstance(result, list)

def test_ls_3(shellEmulator):
    result = shellEmulator.ls()
    assert result is not None
    assert isinstance(result, list)

def test_uname_1(shellEmulator):
    system_info = platform.uname()
    expected = f"{system_info.system} {system_info.node} {system_info.release}"
    result = shellEmulator.uname()
    assert result == expected

def test_uname_2(shellEmulator):
    result = shellEmulator.uname()
    assert result is not None
    assert isinstance(result, str)

def test_uname_3(shellEmulator):
    system_info = platform.uname()
    result = shellEmulator.uname()
    assert f"{system_info.system}" in result

def test_history_1(shellEmulator, capfd):
    shellEmulator.history()
    out, err = capfd.readouterr()
    assert out == ""
    assert err == ""

def test_history_2(shellEmulator, capfd):
    shellEmulator.execute("ls")
    shellEmulator.history()
    out, err = capfd.readouterr()
    assert "ls" in out
    assert err == ""

def test_history_3(shellEmulator, capfd):
    shellEmulator.execute("ls")
    shellEmulator.execute("cd Yesenin_s_dir_1")
    shellEmulator.history()
    out, err = capfd.readouterr()
    assert "ls" in out
    assert "cd Yesenin_s_dir_1" in out
    assert err == ""

@pytest.mark.filterwarnings("ignore::UserWarning")
def test_mv_1(shellEmulator):
    # First create the source file with correct content
    with ZipFile(shellEmulator.fs_zip_path, 'a') as zf:
        zf.writestr("You_were_crying_on_a_quiet_night.txt", b"test content")
    
    shellEmulator.mv("You_were_crying_on_a_quiet_night.txt", "Lovely_night,_I_will_never_retrieve_it.txt")
    assert "Lovely_night,_I_will_never_retrieve_it.txt" in shellEmulator.list_files()
    assert "You_were_crying_on_a_quiet_night.txt" not in shellEmulator.list_files()
    
def test_mv_2(shellEmulator):
    shellEmulator.mv("You_were_crying_on_a_quiet_night.txt", "test_dir/Lovely_night,_I_will_never_retrieve_it.txt")
    assert "Yesenin_s_dir_3/Lovely_night,_I_will_never_retrieve_it.txt" in shellEmulator.list_files()
    assert "You_were_crying_on_a_quiet_night.txt" not in shellEmulator.list_files()

@pytest.mark.filterwarnings("ignore::UserWarning")
def test_mv_3(shellEmulator):
    # First create the source file with correct content
    with ZipFile(shellEmulator.fs_zip_path, 'a') as zf:
        zf.writestr("You_were_crying_on_a_quiet_night.txt", b"test content")
    
    shellEmulator.mv("You_were_crying_on_a_quiet_night.txt", "Yesenin_s_dir_3/I_will_not_deceive_myself,_admitting.txt")
    with ZipFile(shellEmulator.fs_zip_path, 'r') as zf:
        assert zf.read("Yesenin_s_dir_3/I_will_not_deceive_myself,_admitting.txt") == b"test content"
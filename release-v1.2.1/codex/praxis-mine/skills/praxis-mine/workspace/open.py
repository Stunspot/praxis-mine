from pathlib import Path
import os,sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
import praxis_mine as native
os.environ.setdefault('PRAXIS_MINE_HOME',str(native.load_storage().default_home()))
from mine import Mine
from runtime import launch
if __name__=='__main__':launch('praxis-mine','Praxis Mine',Mine,Path(__file__).parent)

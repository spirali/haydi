#####Install distributed
`pip install --user git+git://github.com/dask/distributed.git@master`

#####Download and extract PyPy
1) `wget https://bitbucket.org/squeaky/portable-pypy/downloads/pypy-5.1.1-linux_x86_64-portable.tar.bz2`
2) `tar -xvf pypy-5.1.1-linux_x86_64-portable.tar.bz2`

#####Install virtualenv
1) `pip install --user virtualenvwrapper`
2) `mkdir venv`
3) run and add to `.bashrc` (or other startup script)

```
module load Python/2.7.9-GNU-5.1.0-2.25
source ~/.local/bin/virtualenvwrapper.sh (load virtualenv binaries)
export WORKON_HOME=~/venv (set virtualenv folder)
export PATH=$PATH:~/.local/bin
```
4) `mkvirtualenv -p ~/<pypy_location>/bin/pypy pypy`
5) `workon pypy`
6) `pip install git+git://github.com/dask/distributed.git@master`

######Usage
```
mkvirtualenv <name> - creates virtualenv with the given name
workon <name> - switches to the given virtualenv
deactivate - reverts to system Python
```

#####Run locally
1) `workon pypy`
2) `export PYTHONPATH=<path_to_haydi/src>:<path_to_haydi/apps/dpda>:${PYTHONPATH}`
3) `dscheduler --port <port> &`
4) `dworker --nthreads=1 --nprocs=24 <scheduler hostname>:<scheduler port> &`
5) `deactivate`
6) `python <script>`

#####Run on nodes
1) `workon pypy`
2) `./start-dist.sh`
3) `deactivate`
4) `python <script>`
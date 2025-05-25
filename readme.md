# WRDP

Xfreerdp Wrapper.  

- help: `main.py -h`
- examples: `main.py -he`
- full usage: `main.py -uid=-1`

insert snippet below in ~/.bashrc 
```shell
# source ~/.bashrc && rdppass && echo $rdppass
function rdppass(){
    local value="";
    read -sep 'password: ' value;
    export rdppass=$value;
    echo
}
```
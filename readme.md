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
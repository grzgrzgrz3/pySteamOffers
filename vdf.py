"""
Converting in dirty way vdf(steam client data format) file to json 
"""
import json
import re



def b(str):
    return str.count('"')
    

def value_proces(proc,next):
    # res = re.search('(.*?)"(.*?)".*?"(.*?)"',proc)
    line = ''
    # if l(proc) == l(next):
        # return '%s"%s":   "%s",'%(res.group(1),res.group(2),res.group(3))
    # else:
        # return '%s"%s":   "%s"'%(res.group(1),res.group(2),res.group(3))
    dot = 0
    first = proc.find('"')
    second = proc.find('"',first+1)+1
    line = proc[:second]+':'+proc[second:]
    # line = proc.strip().replace('\t\t',':')
    if '"' in next:
        line += ','
    return line
def l(str):
    t = 0
    for a in str:
        if a == '\t':
            t+= 1
        else:
            return t

        
def convert(unc):
    if isinstance(unc,unicode):
        unc = unc.encode('utf-8')
    opened_q= False
    conv = '{'
    unc = unc.replace('\r','').replace('\\', '/' )
    iter_unc = iter(unc.split('\n'))
    last_line = next(iter_unc)
    conv += last_line+":"
    proc_line = next(iter_unc)
    next_line = ''
    for raw in iter_unc:
        next_line=raw
        while not next_line.replace('\t','').replace(' ',''):
            # print [next_line]
            try:
                next_line = next(iter_unc)
            except StopIteration:
                break
        if "{" in proc_line and not '"' in proc_line:
            conv+= proc_line
        elif b(proc_line) == 2:
            conv+=proc_line
            conv+=":"
        elif b(proc_line) == 4:
            conv+= value_proces(proc_line,next_line)
                
        elif "}" in proc_line:
            # if l(proc_line) == l(next_line):
            if not '}' in next_line and '"' in next_line:
                proc_line+= ","
            conv+= proc_line
            
        else:
            print [proc_line]
            pass
        conv+='\n'
        last_line = proc_line
        proc_line = next_line
    conv+= next_line
    conv+= "}"
    return json.loads(conv)

if __name__ == "__main__":
    f = open('game_schema_570.vdf').read()
    f = convert(f)

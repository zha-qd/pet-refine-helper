import ast,runpy
from pathlib import Path
ns=runpy.run_path(str(Path(__file__).resolve().parent / 'test_verification.py'))
trial=ns['trial']
for value in [.12,-.12,0]:
    a,clicks,logs=trial('单洗','盾兵生命',[(3375,4469)],[value])
    assert '第 1 次洗炼' in logs
    assert any('替换' in line if value>0 else '重洗' in line for line in logs)
    if value: assert any(f'{value:+.2f}%' in line for line in logs)
    if value<=0: assert clicks==['refine','reroll']
t=ast.parse((Path(__file__).resolve().parents[1] / 'auto_refine_gui.py').read_text(encoding='utf-8'))
c=next(n for n in t.body if isinstance(n,ast.ClassDef) and n.name=='RefineApp')
method=next(n for n in c.body if isinstance(n,ast.FunctionDef) and n.name=='_get_value')
env={}; exec(compile(ast.Module(body=[method],type_ignores=[]),'zero','exec'),env)
from types import SimpleNamespace as N
logs=[]
a=N(_abs_region=lambda name:None,_grab=lambda region:None,_detect_sign=lambda img:0,
    log=lambda msg:logs.append(msg),stat_ocr_fail=0)
assert env['_get_value'](a,'盾兵生命')==(0.0,True)
assert a.stat_ocr_fail==0 and logs==['  盾兵生命: 无变化']
print('PASS: zero change needs no OCR, no OCR failure increment, per-round and signed-value logs, nonpositive reroll')

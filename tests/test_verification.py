import ast,re
from pathlib import Path
from types import SimpleNamespace as N
t=ast.parse((Path(__file__).resolve().parents[1] / 'auto_refine_gui.py').read_text(encoding='utf-8'))
c=next(n for n in t.body if isinstance(n,ast.ClassDef) and n.name=='RefineApp')
c.body=[n for n in c.body if isinstance(n,ast.FunctionDef) and n.name in ['_parse_total','_expected_totals','_read_totals','_worker','_selected_attributes','_record_gains','_should_replace']]
env={'re':re,'time':N(sleep=lambda x:None),'mss':lambda:N(close=lambda:None)}
exec(compile(ast.Module(body=[c],type_ignores=[]),'totals','exec'),env); A=env['RefineApp']
assert A._parse_total('33.75%/44.69%')==(3375,4469)
for bad in ['33.75','33.75/44.69','45%/44.69%','abc','0%/0%']:
    assert A._parse_total(bad) is None
assert A._expected_totals({'x':(4460,4469)},['x'],[.12])=={'x':(4469,4469)}
a=A(); a.running=True; a._wait_running=lambda x:True
reads=iter([(3375,4469),(3387,4469),(3387,4469)])
a._get_total=lambda n:next(reads)
assert a._read_totals(['x'],expected={'x':(3387,4469)},finish=True)=={'x':(3387,4469)}
a._get_total=lambda n:(3375,4469)
assert a._read_totals(['x'],expected={'x':(3387,4469)},finish=True) is None
def trial(mode,sub,before,delta,verified=True):
    a=A(); a.run_mode=mode; a.run_sub=sub; a.running=True
    keys=a._selected_attributes(mode,sub)
    a.attribute_gains=dict.fromkeys(keys,0.); a.stat_total=a.stat_replaced=a.stat_rerolled=0
    a.var_anim_delay=N(get=lambda:0); a._wait_running=lambda t:a.running
    logs=[]; clicks=[]; a.log=lambda msg,*tag:logs.append(msg)
    a._update_stats=lambda:None; a._stop=lambda:None; a.root=N(after=lambda *x:None)
    def read(names,expected=None,finish=False):
        if expected is not None:
            a.running=False
            return expected if verified else None
        return dict(zip(keys,before))
    a._read_totals=read
    a._get_value=lambda name:(delta[keys.index(name)],True)
    def click(name,**kw):
        clicks.append(name)
        if name=='reroll': a.running=False
        return True
    a._safe_click=click; a._worker()
    return a,clicks,logs
a,clicks,logs=trial('单洗','盾兵生命',[(4469,4469)],[.12]); assert not clicks and any('已满' in x for x in logs)
a,clicks,logs=trial('单洗','盾兵生命',[(3375,4469)],[.12]); assert a.attribute_gains['盾兵生命']==.12 and a.stat_replaced==1
a,clicks,logs=trial('单洗','盾兵生命',[(3375,4469)],[.12],False); assert a.stat_replaced==0 and a.attribute_gains['盾兵生命']==0 and clicks==['refine','replace','confirm']
a,clicks,logs=trial('单洗','盾兵生命',[(4460,4469)],[.12]); assert a.attribute_gains['盾兵生命']==.09 and any('达到上限' in x for x in logs)
a,clicks,logs=trial('双洗','射手双洗',[(3375,4469),(3130,4469)],[.12,-.02]); assert list(a.attribute_gains.values())==[.12,0]
a,clicks,logs=trial('三洗','矛兵三洗',[(3375,4469),(763,1341),(845,1341)],[.12,-.02,.03]); assert list(a.attribute_gains.values())==[.12,0,.03]
print('PASS: strict parser, stable delayed reads, mismatch stop, initial full stop, verified gain, capped gain, single/dual/triple modes')

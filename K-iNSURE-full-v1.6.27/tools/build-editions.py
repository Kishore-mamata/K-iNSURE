# Builds K-iNSURE-P.html (public), K-iNSURE-BAGS.html (agents) and K-iNSURE.html (owner desktop) from index.html.
# Run from the app folder: python3 tools/build-editions.py
import re,json
src=open('index.html',encoding='utf-8').read()

def cut(s,a,e):
    i=s.find(a); assert i>=0,a; j=s.find(e,i); assert j>=0; return s[:i]+s[j+len(e):]
def rep(s,a,b,n=1):
    assert s.count(a)==n,(s.count(a),a[:70]); return s.replace(a,b)

ED={
 'P':   dict(file='K-iNSURE-P.html',name='K-iNSURE-P',short='K-iNSURE-P',sub='PUBLIC EDITION',badge='PUBLIC',color='#8FB3F5',
             h1='Welcome to K-iNSURE',lead='Quick, clear premium quotes for Motor, Fire and Health insurance.',
             desc='Free premium calculator for Motor, Fire and Health insurance.'),
 'BAGS':dict(file='K-iNSURE-BAGS.html',name='K-iNSURE-BAGS',short='K-iNSURE BAGS',sub='AGENTS EDITION',badge='AGENTS',color='#FFC21A',
             h1='Welcome, Agent',lead='Premium calculators for Motor, Fire and Health, plus your remuneration.',
             desc='K-iNSURE for insurance agents: premium calculators and remuneration.'),
 'D':   dict(file='K-iNSURE.html',name='K-iNSURE',short='K-iNSURE',sub='OWNER DESKTOP',badge='OWNER DESKTOP',color='#FFC21A',
             h1='Welcome to K-iNSURE',lead='Owner desktop: calculators, remuneration, tariffs, quotations and settings.',
             desc='K-iNSURE owner desktop edition.'),
}
manifest=json.load(open('manifest.webmanifest'))

for k,e in ED.items():
    s=src
    s=rep(s,'<title>K-iNSURE SUITE</title>',f'<title>{e["name"]}</title>')
    mf=f'manifest-{k.lower()}.webmanifest'
    s=rep(s,'<link rel="manifest" href="manifest.webmanifest">',f'<link rel="manifest" href="{mf}">')
    m=dict(manifest); m.update(name=e['name'],short_name=e['short'],description=e['desc'],id='./'+e['file'],start_url='./'+e['file'],theme_color='#0B1730'); m.pop('shortcuts',None)
    open(mf,'w').write(json.dumps(m,indent=2,ensure_ascii=False)+'\n')
    s=rep(s,'<div class="brandtext">K-iNSURE<small>INSURANCE SUITE</small></div></div>',
            f'<div class="brandtext">K-iNSURE<small>{e["sub"]}</small></div></div>\n  <div class="k-edition">{e["badge"]}</div>')
    s=rep(s,'<div class="topline"><div class="kinsure"><span>K-iNSURE SUITE</span></div></div>',
            f'<div class="topline"><div class="kinsure"><span>{e["name"]}</span><em class="k-edition-top">{e["badge"]}</em></div></div>')
    s=rep(s,'<h1>Welcome to K-iNSURE</h1><div class="sub">One workspace for Motor, Fire and Health premium calculations.</div>',
            f'<h1>{e["h1"].replace("K-iNSURE","K&#8209;iNSURE")}</h1><div class="sub">{e["lead"]}</div>')
    s=rep(s,"var appLink=location.origin+location.pathname.replace(/[^\\/]*$/,'')+(isMobile?'mobile.html':'');",
            "var appLink=location.origin+location.pathname;")
    if k in('P','BAGS'):
        # no owner access at all
        s=rep(s,'<script src="owner-key.js"></script>\n','')
        s=cut(s,'<script id="kinsure-owner-entry">','</script>')
        # v1.6.18: Public/Agents always mirror the published rates and have no Publish panel
        s=rep(s,'var OWNER_ED=true; /*K-EDITION*/','var OWNER_ED=false; /*K-EDITION*/')
        s=cut(s,'<script id="kinsure-publish">','</script>')
        # public-friendly dashboard
        s=rep(s,'''<div class="metric"><small>SHARED WORKSPACE</small><strong>Quotations &amp; Settings</strong></div>''',
               '<div class="metric"><small>SHARE</small><strong>WhatsApp &amp; print</strong></div>' if k=='P' else
               '<div class="metric"><small>REMUNERATION</small><strong>Commission &amp; incentive</strong></div>')
        s=rep(s,'''<div class="metric"><small>CALCULATION DESIGN</small><strong>Independent engines</strong></div>''',
               '<div class="metric"><small>PRIVACY</small><strong>Data stays on your device</strong></div>')
        i=s.find('<div class="panel"><h3>Design &amp; Integration Principles</h3>'); j=s.find('</div>\n    </section>',i); assert i>0 and j>i
        third=('<div class="principle"><strong>03 · Private by design</strong><small>Customer details stay on your own phone or computer. Nothing is sent to us.</small></div>' if k=='P' else
               '<div class="principle"><strong>03 · Remuneration for agents</strong><small>Commission and incentive tables open with your Agent access code.</small></div>')
        s=s[:i]+('<div class="panel"><h3>How K-iNSURE helps</h3>\n'
          '        <div class="principle"><strong>01 · Quick quotes</strong><small>Enter the vehicle or property details and get the premium breakdown instantly.</small></div>\n'
          '        <div class="principle gold"><strong>02 · Share with customers</strong><small>Send the quotation on WhatsApp or print it as a PDF.</small></div>\n'
          '        '+third+'\n      ')+s[j:]
        s=rep(s,'<div class="note">Integrated shell: Motor and Fire open their original calculator files as separate modules.</div>',
                '<div class="note">Quotations are indicative and subject to the insurer\'s underwriting, acceptance and policy terms.</div>')
    if k=='P':
        s=rep(s,'    <button data-page="Incentives" onclick="kinsureIncentives(this)"><span class="ico">💰</span><span class="txt">Remuneration</span></button>\n','')
        s=cut(s,'<script src="remuneration-data.js"></script>','</script>')  # removes the src tag line only
        s=cut(s,'<script id="kinsure-remuneration-lock">','</script>')
        s=cut(s,'<style id="kinsure-incentives-style">','</style>')
        s=s.replace('window.kinsureIncentives','window.kinsureIncentives')  # nothing else references it
    if k=='BAGS':
        s=rep(s,'''<button class="open" onclick="openModule('health.html')">Open Health Calculator →</button></div></article>''',
                '''<button class="open" onclick="openModule('health.html')">Open Health Calculator →</button></div></article>
      <article class="module k-rem-card"><div class="moduleicon">💰</div><div class="modinfo"><h2>Remuneration</h2><p>Commission by state · Fire, Engineering &amp; Marine Hull · Incentive</p><button class="open" onclick="kinsureIncentives(document.querySelector('.nav button[data-page=&quot;Incentives&quot;]'))">Open Remuneration →</button></div></article>''')
    if k=='D':
        s=rep(s,'<div class="sidefoot">','<button type="button" class="k-owner-btn" id="kOwnerBtn" onclick="kinsureRole===\'owner\'?selectRole(\'user\'):selectRole(\'owner\')">🔑 Owner sign-in</button>\n  <div class="sidefoot">')
    css=f'''
<style id="kinsure-edition">
/* {e["name"]}: edition badge and layout touches */
.k-edition{{margin:2px 14px 10px;padding:5px 10px;border-radius:999px;font:800 11px/1.2 system-ui,sans-serif;letter-spacing:.12em;text-align:center;background:{e["color"]};color:#0B1730}}
.topline .kinsure{{display:flex;align-items:center;gap:10px}}
.k-edition-top{{font-style:normal;padding:3px 9px;border-radius:999px;font:800 10px/1.2 system-ui,sans-serif;letter-spacing:.1em;background:{e["color"]};color:#0B1730}}
html:not(#z1):not(#z2):not(#z3):not(#z4):not(#z5):not(#z6) body #dashboardView .cards .k-rem-card{{grid-column:1/-1;border-top:4px solid #FFC21A!important;background:linear-gradient(110deg,#0B1730,#22365F)!important}}
html:not(#z1):not(#z2):not(#z3):not(#z4):not(#z5):not(#z6) body #dashboardView .cards .k-rem-card h2{{color:#FFC21A!important}}
html:not(#z1):not(#z2):not(#z3):not(#z4):not(#z5):not(#z6) body #dashboardView .cards .k-rem-card p{{color:#dbe4f3!important}}
html:not(#z1):not(#z2):not(#z3):not(#z4):not(#z5):not(#z6) body #dashboardView .cards .k-rem-card .moduleicon{{background:#FFF3C4!important}}
.k-owner-btn{{margin:8px 14px 4px;padding:9px 12px;border-radius:10px;border:1px solid {e["color"]};background:transparent;color:#fff;font:700 13px system-ui,sans-serif;cursor:pointer;text-align:left}}
.k-owner-btn.on{{background:{e["color"]};color:#0B1730}}
@media (max-width:760px){{.k-edition{{display:none}}.k-owner-btn{{display:none}}}}
</style>
'''
    if k=='D':
        css+='''<script id="kinsure-owner-btn">
(function(){var o=window.updateRoleUI;window.updateRoleUI=updateRoleUI=function(){var r=o.apply(this,arguments);var b=document.getElementById('kOwnerBtn');if(b){var on=kinsureRole==='owner';b.textContent=on?'🔓 Owner · Sign out':'🔑 Owner sign-in';b.classList.toggle('on',on);}return r;};updateRoleUI();})();
</script>
'''
    k2=s.rfind('</body>'); s=s[:k2]+css+s[k2:]
    open(e['file'],'w',encoding='utf-8').write(s)
    print(e['file'],len(s))

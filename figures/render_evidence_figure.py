"""Render a data-derived table/summary, not a fabricated application screenshot."""
from pathlib import Path
import hashlib
import html
import json
import re
from PIL import Image, ImageDraw, ImageFont

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
W,H=2100,1280
image=Image.new('RGB',(W,H),'white')
draw=ImageDraw.Draw(image)
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     '<rect width="100%" height="100%" fill="white"/>']


def font(size,bold=False):
    choices=[Path('C:/Windows/Fonts')/('timesbd.ttf' if bold else 'times.ttf'),
             Path('DejaVuSerif-Bold.ttf' if bold else 'DejaVuSerif.ttf')]
    for choice in choices:
        try:return ImageFont.truetype(str(choice),size)
        except OSError:pass
    raise RuntimeError('Install Times New Roman or DejaVu Serif to render the figure')


def text(x,y,value,size=34,bold=False,fill='#111111',anchor=None):
    f=font(size,bold)
    if anchor=='middle':x-=draw.textlength(value,font=f)/2
    draw.text((x,y),value,font=f,fill=fill)
    svg.append(f'<text x="{x:.1f}" y="{y+size*.84:.1f}" font-family="Times New Roman,serif" '
               f'font-size="{size}" font-weight="{700 if bold else 400}" fill="{fill}">'
               f'{html.escape(value)}</text>')


def rect(x0,y0,x1,y1,fill='white',outline='#111111',width=2):
    draw.rectangle((x0,y0,x1,y1),fill=fill,outline=outline,width=width)
    svg.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" '
               f'fill="{fill}" stroke="{outline}" stroke-width="{width}"/>')


def line(x0,y0,x1,y1,width=2):
    draw.line((x0,y0,x1,y1),fill='#333333',width=width)
    svg.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="#333333" stroke-width="{width}"/>')


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    primary=json.loads((ROOT/'evidence/results.json').read_text(encoding='utf-8-sig'))
    audit=json.loads((ROOT/'review/execution_final/audit_results.json').read_text(encoding='utf-8-sig'))
    demo=(ROOT/'evidence/demo.log').read_text(encoding='utf-8-sig')
    assert primary['passed']==49 and primary['failed']==0
    assert primary['behavioural_cases']==40 and primary['expected_negative_cases']==9
    assert audit['all_passed'] and len(audit['results'][0]['observed_true'])==24
    observed=re.findall(r'mk_Evaluacion\((<\w+>), (<\w+>), (nil|<\w+>), (\d+),',demo)
    expected=[('<Verde>','<SinDatos>','nil','4'),('<Rojo>','<Vigente>','<Rojo>','5'),
              ('<Rojo>','<Vigente>','<Verde>','6'),('<Rojo>','<Vigente>','<Verde>','6'),
              ('<Verde>','<Vigente>','<Verde>','7')]
    assert observed==expected,observed
    text(50,34,'Evidencia ejecutada del modelo VDM++ 2.0.0',54,True)
    text(50,111,'Datos sintéticos · VDMJ 4.7.0 (build 260414) · Java 18.0.1',34)
    cards=[('40/40','comportamientos retornan true'),
           ('9/9','rechazos contractuales esperados'),
           ('24/24','verificaciones independientes')]
    for index,(value,label) in enumerate(cards):
        left=50+index*680
        rect(left,180,left+640,350,fill='#f4f4f4',outline='#777777')
        text(left+320,195,value,72,True,anchor='middle')
        text(left+320,287,label,32,anchor='middle')
    text(50,390,'Traza observada: retención y descenso autorizado',40,True)
    columns=[50,170,1025,1875,2050]
    top=465;header=74;row_height=89
    rect(columns[0],top,columns[-1],top+header+5*row_height,outline='#222222')
    rect(columns[0],top,columns[-1],top+header,fill='#e9e9e9',outline='#222222')
    headings=['Paso','Entrada o acción','Nivel | Calidad | Candidato','Versión']
    for i,label in enumerate(headings):
        text(columns[i]+15,top+18,label,32,True)
    actions=['Inventario de 1 sensor; reloj lógico = 100',
             'Lectura 1: h = 80%; i = 4°; t = 99',
             'Lectura 2: h = 40%; i = 3°; t = 100',
             'RegistrarConfirmacion; lectura 2, versión 6',
             'AplicarDescenso; autorización consumida']
    for index,(level,quality,candidate,version) in enumerate(observed):
        y=top+header+index*row_height
        if index:line(columns[0],y,columns[-1],y,width=1)
        text(columns[0]+37,y+24,str(index+1),34)
        text(columns[1]+15,y+24,actions[index],33)
        state=' | '.join([level.strip('<>'),quality.strip('<>'),candidate.strip('<>')])
        text(columns[2]+15,y+24,state,34,bold=index in {1,2,4})
        text(columns[3]+40,y+24,version,34)
    for x in columns[1:-1]:line(x,top,x,top+header+5*row_height,width=1)
    text(50,1015,'La entrada crítica crea 2 avisos Pendiente; el descenso no los elimina.',33)
    text(50,1065,'Precondiciones · postcondiciones · invariantes · tipos dinámicos: ACTIVADOS.',33,True)
    text(50,1115,'80 obligaciones generadas; 0 descargadas: 53 Unchecked y 27 Unproved.',33)
    text(50,1177,'Síntesis de logs reales: no es una captura de interfaz ni validación geotécnica.',31)
    svg.append('</svg>')
    (HERE/'fig_evidence_vdmpp_v2.svg').write_text('\n'.join(svg),encoding='utf-8')
    image.save(HERE/'fig_evidence_vdmpp_v2.png',dpi=(300,300))
    sources=['evidence/results.json','evidence/demo.log','review/execution_final/audit_results.json',
             'evidence/proof_obligations.log']
    metadata={'type':'Data-derived evidence summary table; not UI screenshot',
      'model_version':'2.0.0','published':False,
      'caption_proposed_es':'Síntesis de la validación ejecutada del modelo VDM++ 2.0.0 y traza de '
        'retención y descenso autorizado. Se distinguen 40 comportamientos conformes, 9 rechazos '
        'contractuales esperados y 24 verificaciones adicionales de auditoría; estas últimas no '
        'constituyen escenarios del dominio necesariamente disjuntos. Datos sintéticos. Las '
        '80 obligaciones generadas permanecen sin descargar. Elaboración a partir de logs del '
        'intérprete, no captura de una interfaz ni evidencia de campo.',
      'sources':{name:digest(ROOT/name) for name in sources},
      'render_method':'Pillow and equivalent SVG from immutable JSON/log observations; verifies '
        'all five snapshots before rendering; no generative image editing or fabricated UI.',
      'observed_trace':[{'nivel':a,'calidad':b,'candidato':c,'version':int(d)} for a,b,c,d in observed]}
    (HERE/'evidence_figure_metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Rendered verified evidence figure PNG+SVG; five observed snapshots matched.')


if __name__=='__main__':main()

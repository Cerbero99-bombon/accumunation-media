import json,sys
def ts(t):
    h=int(t//3600); m=int(t%3600//60); s=t%60
    return "%d:%02d:%05.2f"%(h,m,s)
def build(words, out, res=(1080,1920), group=3):
    hdr=f"""[Script Info]
ScriptType: v4.00+
PlayResX: {res[0]}
PlayResY: {res[1]}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Pop,DejaVu Sans,96,&H00FFFFFF,&H000000FF,&H00101010,&H90000000,-1,0,0,0,100,100,0,0,1,7,3,5,80,80,150,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    lines=[]
    for i in range(0,len(words),group):
        g=words[i:i+group]
        st=g[0][0]; en=g[-1][1]
        # karaoke: evidenzia la parola corrente
        for j,(ws,we,wt) in enumerate(g):
            parts=[]
            for k,(_,_,t2) in enumerate(g):
                parts.append(r"{\c&H00FFFF&\fscx108\fscy108}"+t2+r"{\c&HFFFFFF&\fscx100\fscy100}" if k==j else t2)
            lines.append("Dialogue: 0,%s,%s,Pop,,0,0,0,,%s"%(ts(ws),ts(we)," ".join(parts)))
    open(out,"w").write(hdr+"\n".join(lines)+"\n")
    return len(lines)
if __name__=="__main__":
    w=json.load(open(sys.argv[1]))
    print("righe ASS:",build([tuple(x) for x in w], sys.argv[2]))

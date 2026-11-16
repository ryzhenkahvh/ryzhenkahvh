#!/usr/bin/env python3
import json, os, random, re, sys
from pathlib import Path
from urllib.parse import urlencode

N=5
STATE=Path('signal-grid.json')
README=Path('README.md')
BEGIN='<!-- SIGNAL-GRID:START -->'
END='<!-- SIGNAL-GRID:END -->'
REPO='ryzhenkahvh/ryzhenkahvh'

def toggle(board, row, col):
    for dr,dc in ((0,0),(1,0),(-1,0),(0,1),(0,-1)):
        r,c=row+dr,col+dc
        if 0<=r<N and 0<=c<N: board[r*N+c] ^= 1

def puzzle(round_number):
    rng=random.Random(73519+round_number)
    while True:
        board=[0]*25
        for index in rng.sample(range(25), 10): toggle(board,index//5,index%5)
        if sum(board)>=8: return board

def new_state(): return {'round':1,'version':0,'moves':0,'board':puzzle(1),'last':'—'}
def valid(s):
    return (type(s.get('round')) is int and s['round']>0 and type(s.get('version')) is int and s['version']>=0 and type(s.get('moves')) is int and s['moves']>=0 and isinstance(s.get('board'),list) and len(s['board'])==25 and all(type(x) is int and x in (0,1) for x in s['board']))

def render(s):
    out=['### SIGNAL GRID','',f"**Round {s['round']}** · Moves: {s['moves']} · Last: {s['last']}",'', 'Turn off all lights. A move flips one cell and its four neighbours.', '', 'Click a cell → submit the prefilled issue → wait for the board to update.', '', '| | A | B | C | D | E |','|:--:|:--:|:--:|:--:|:--:|:--:|']
    for r in range(N):
        cells=[]
        for c in range(N):
            title=f'SIGNAL {s["version"]} {r} {c}'
            url=f'https://github.com/{REPO}/issues/new?'+urlencode({'title':title,'body':'Submit this issue to play your move.'})
            cells.append(f'[{"🟪" if s["board"][r*N+c] else "⬛"}]({url})')
        out.append('| '+str(r+1)+' | '+' | '.join(cells)+' |')
    out += ['','<sub>One shared game · GitHub account required · stale moves are rejected</sub>','']
    return '\n'.join(out)

def main():
    mode=sys.argv[1]
    state=json.loads(STATE.read_text()) if STATE.exists() else new_state()
    if not valid(state): raise ValueError('Invalid game state')
    if mode=='move':
        event=json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text()); issue=event['issue']; title=issue['title']
        m=re.fullmatch(r'SIGNAL (\d{1,10}) ([0-4]) ([0-4])',title)
        if not m: print('IGNORE'); return
        version,row,col=map(int,m.groups())
        if version!=state['version']:
            Path('signal-result.txt').write_text('This move is stale. Refresh the profile and try again.'); print('STALE'); return
        toggle(state['board'],row,col);state['version']+=1;state['moves']+=1
        actor=issue['user']['login']
        if not re.fullmatch(r'[A-Za-z0-9-]{1,39}',actor): actor='player'
        if not any(state['board']):
            completed=state['round'];moves=state['moves'];state['round']+=1;state['moves']=0;state['board']=puzzle(state['round']);state['last']=f'@{actor} solved round {completed} in {moves} moves'
            result=f'Grid solved! Round {completed} completed in {moves} moves. A new round is ready.'
        else:
            state['last']=f'@{actor} · {chr(65+col)}{row+1}'; result=f'Move {chr(65+col)}{row+1} accepted. The board has been updated.'
        Path('signal-result.txt').write_text(result)
    elif mode!='init': raise ValueError('Unknown mode')
    STATE.write_text(json.dumps(state,indent=2)+'\n')
    text=README.read_text();section=BEGIN+'\n'+render(state)+END
    if BEGIN in text and END in text: text=text[:text.index(BEGIN)]+section+text[text.index(END)+len(END):]
    else: text=text.rstrip()+'\n\n'+section+'\n'
    README.write_text(text)
if __name__=='__main__': main()

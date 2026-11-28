"""Plotly figures that require no external map tiles or network services."""
from html import escape
from textwrap import wrap
import plotly.graph_objects as go

ISO={'India':'IND','China':'CHN','USA':'USA','Japan':'JPN','Germany':'DEU','Australia':'AUS'}
CENTERS={'India':(79,23),'China':(104,35),'USA':(-99,39),'Japan':(138,37),'Germany':(10,51),'Australia':(135,-25)}
COLORS={'Lower':'#82c8b6','Moderate':'#efc46e','Higher':'#e58e88'}


def style(fig, height=410):
    fig.update_layout(template='plotly_white',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='#ffffff',
        font=dict(color='#203a40',size=13),height=height,margin=dict(l=20,r=20,t=30,b=40),
        legend=dict(orientation='h',y=1.03))
    fig.update_xaxes(gridcolor='#dce6e3',automargin=True)
    fig.update_yaxes(gridcolor='#dce6e3',automargin=True)
    return fig


def coordinates(shapes):
    x=[]; y=[]
    for shape in shapes:
        for ring in shape['rings']:
            x.extend([p[0] for p in ring]+[None]); y.extend([p[1] for p in ring]+[None])
    return x,y


def exposure_map(outlines, rows, active_country):
    fig=go.Figure()
    x,y=coordinates(outlines)
    fig.add_scatter(x=x,y=y,mode='lines',fill='toself',fillcolor='#e2ebe8',line=dict(color='#a0b8b1',width=.45),hoverinfo='skip',showlegend=False)
    for level,color in COLORS.items():
        members=[r for r in rows if r['level']==level]
        shapes=[p for p in outlines if p['iso'] in [ISO[r['country']] for r in members]]
        x,y=coordinates(shapes)
        if shapes:
            fig.add_scatter(x=x,y=y,mode='lines',fill='toself',fillcolor=color,line=dict(color='#738c84',width=.7),name=level,hoverinfo='skip',legendgroup=level,showlegend=True)
        for r in members:
            country=r['country']; lon,lat=CENTERS[country]; active=country==active_country
            info='<br>'.join(escape(t) for t in wrap(r['rationale'],55))
            fig.add_scatter(x=[lon],y=[lat],mode='markers+text',text=[country],textposition='top center',
                textfont=dict(color='#142d33',size=12),marker=dict(size=14 if active else 8,color=color,line=dict(color='#ffffff' if active else '#101a29',width=2 if active else 1)),
                hovertemplate=f'<b>{country}</b> · {level}<br>{info}<extra></extra>',showlegend=False,legendgroup=level)
    style(fig,460)
    fig.update_layout(dragmode='pan',hovermode='closest',legend_title_text='Qualitative sensitivity')
    fig.update_xaxes(visible=False,range=[-180,180],constrain='domain')
    fig.update_yaxes(visible=False,range=[-60,85],scaleanchor='x',scaleratio=1,constrain='domain')
    return fig


def transmission(chain, macro, industry, channel, risk):
    """Equal-width links are conceptual connections, not measured flows."""
    raw=list(chain)+['Macroeconomic outcomes','Industry: '+industry,channel,risk]
    n=len(chain)
    labels=['<br>'.join(escape(t) for t in wrap(s,30)) for s in raw]
    src=list(range(n-1))+[n-1,n-2,n+1,n+2]
    dst=list(range(1,n))+[n,n+1,n+2,n+3]
    hover=list(chain)+['<br>'.join(escape(t) for t in macro),industry,channel,risk]
    fig=go.Figure(go.Sankey(arrangement='snap',node=dict(label=labels,pad=22,thickness=18,
       color=['#78cfc5']*(n-1)+['#efc46e','#8caee6','#efc46e','#efc46e','#e58e88'],
       customdata=hover,hovertemplate='%{customdata}<extra></extra>'),
       link=dict(source=src,target=dst,value=[1]*len(src),color='rgba(12,122,104,.23)',hovertemplate='Illustrative connection (no measured magnitude)<extra></extra>')))
    return style(fig,410)


def scenario_chart(rows,currency):
    fig=go.Figure()
    fig.add_bar(x=[r['Scenario'] for r in rows],y=[r['Baseline'] for r in rows],name='Baseline',marker_color='#087668')
    fig.add_bar(x=[r['Scenario'] for r in rows],y=[r['Scenario cost'] for r in rows],name='Scenario cost',marker_color=['#8caee6','#efc46e','#e58e88'])
    fig.update_layout(barmode='group',yaxis_title=f'Cost ({currency})')
    return style(fig,360)


def sensitivity_chart(rows,currency):
    fig=go.Figure(go.Bar(x=[r['Additional cost'] for r in rows],y=[r['Input'] for r in rows],orientation='h',marker_color='#087668',hovertemplate=currency+' %{x:,.2f}<extra></extra>'))
    fig.update_layout(xaxis_title=f'Additional cost ({currency})')
    return style(fig,320)

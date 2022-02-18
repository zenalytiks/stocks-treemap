import pandas as pd
import plotly.graph_objects as go
import json
import requests
import dash
from dash import dcc
from dash import html

app = dash.Dash(__name__)

f = open('ts.json')
res = json.load(f)

df = pd.DataFrame.from_dict(pd.json_normalize(res), orient='columns')



df['total'] = pd.to_numeric(df['total'])

red_df = df[df['put_call'] == 'PUT']
red_mean = red_df['total'].mean()

green_df = df[df['put_call'] == "CALL"]
green_mean = green_df['total'].mean()


labels = []
values = []
parents = []
text = []
colors_list = []

frames = []


for ticker in df['ticker'].unique():
    df_filtered = df[df['ticker'] == ticker]
    if len(df_filtered) > 1:
        frames.append(df_filtered)
    else:
        if "PUT" not in df_filtered['put_call'].tolist():
            new_row = {'total':0,'put_call':'PUT','ticker':ticker}
            df_filtered = df_filtered.append(new_row,ignore_index=True)
            frames.append(df_filtered)
        if "CALL" not in df_filtered['put_call'].tolist():
            new_row = {'total':0,'put_call':'CALL','ticker':ticker}
            df_filtered = df_filtered.append(new_row,ignore_index=True)
            frames.append(df_filtered)


df = pd.concat(frames,ignore_index=True)



for ticker in df['ticker'].unique():
    df_filtered = df[df['ticker'] == ticker]
    df_filtered.reset_index(inplace=True)
    values.append(df_filtered['total'].sum())
    labels.append(ticker)
    parents.append(" ")
    df_put= df_filtered[df_filtered['put_call'] == 'PUT']
    df_call = df_filtered[df_filtered['put_call'] == 'CALL']
    df_put.reset_index(inplace=True)
    df_call.reset_index(inplace=True)

    if (not df_put.empty) and (not df_call.empty):
        if (df_call['total'][0] > 2*df_put['total'][0]):

            if (df_call['total'][0] - df_put['total'][0]) >= green_mean:
                text.append(str(df_call['total'][0])+"/"+str(df_put['total'][0]))
                colors_list.append('#4cc9b7')


            elif (df_call['total'][0] - df_put['total'][0]) <= green_mean:
                text.append(str(df_call['total'][0])+"/"+str(df_put['total'][0]))
                colors_list.append('#b2e8e0')


        elif (df_put['total'][0] > 2*df_call['total'][0]):
            if (df_put['total'][0] - df_call['total'][0]) >= red_mean:
                text.append(str(df_call['total'][0])+"/"+str(df_put['total'][0]))
                colors_list.append("#ff6d92")
            elif (df_put['total'][0] - df_call['total'][0]) <= red_mean:
                text.append(str(df_call['total'][0])+"/"+str(df_put['total'][0]))
                colors_list.append("#ffc0d0")



        else:
            text.append(str(df_call['total'][0])+"/"+str(df_put['total'][0]))
            colors_list.append("#7252E6")


green_color_index_list = []
green_color_values = []
red_color_index_list = []
red_color_values = []
for i,color in enumerate(colors_list):
    if colors_list[i] == "#4cc9b7":
        green_color_index_list.append(i)

for i,color in enumerate(colors_list):
    if colors_list[i] == "#ff6d92":
        red_color_index_list.append(i)

for color_index in green_color_index_list:
    green_color_values.append(values[color_index])

for color_index in red_color_index_list:
    red_color_values.append(values[color_index])

if green_color_values:
    green_max_index = values.index(max(green_color_values))
    colors_list[green_max_index] = "#008f7a"

if red_color_values:
    red_max_index = values.index(max(red_color_values))
    colors_list[red_max_index] = "#e52a5a"

fig = go.Figure(go.Treemap(
    labels = labels,
    values = values,
    parents = parents,
    text = text,
    marker= dict(colors=colors_list,pad=dict(l=0,r=0,t=0,b=0)),
    pathbar= dict(visible = False),
    tiling=dict(pad=0)
))

fig.update_layout(
    plot_bgcolor="#1A1A27",
    paper_bgcolor="#1A1A27",
    margin=dict(l=0,r=0,b=0,t=0)

)
fig.layout.images = [dict(
        source="https://i.ibb.co/y6PVjyn/logo.png",
        xref="paper", yref="paper",
        x=1, y=-0.09,
        sizex=0.08, sizey=0.08,
        xanchor="center", yanchor="bottom"
      )]
fig.write_html("index.html")

app.layout = html.Div(id='container',
                      children=[
                      dcc.Graph(figure=fig,
                      config=dict(
                      toImageButtonOptions=dict(format='png',filename='treemap',height=2160,width=3840)),
                      style={'position':'fixed','width':'100%','height':'100%','top':'0px','left':'0px'})

                      ],style={'background-color':'#1A1A27','position':'fixed','width':'100%','height':'100%','top':'0px','left':'0px'}
            )

if __name__ == '__main__':
    app.run_server(debug=False)

import pandas as pd
import plotly.graph_objects as go


def ScientificPlot():
    file_path = 'data/ScientificMeasurements.csv'
    df = pd.read_csv(file_path, sep=';')
    fig = go.Figure()
    colors = ['#37474F', '#0077B6', '#7C7F85', '#E63946',
              '#43AA8B', '#6A0572', '#D97941', '#3D5A80', '#FFB703']

    th_columns = [col for col in df.columns if 'TH' in col]
    for i, col in enumerate(th_columns):
        fig.add_trace(go.Scatter(
            x=df['T'],
            y=df[col],
            mode='lines',
            line=dict(color=colors[i], shape='spline'),
            name=col,
            hovertemplate='%{y:.1f}°C'
        ))

    fig.add_trace(go.Scatter(
        x=df['T'],
        y=df['Photodiode'],
        mode='lines',
        name='Photodiode',
        line=dict(color=colors[-1], shape='spline', dash='dot'),
        yaxis='y2',
        hovertemplate='%{y:.1f} mV'
    ))

    fig.update_layout(
        title={
            'text': 'PariSat Scientific Measurements • Ariane 6 Flight VA262 (July 9, 2024)',
            'x': 0.5,
            'xanchor': 'center',
            'y': 0.9,
            'yanchor': 'bottom'
        },
        xaxis_title='Time (s)',
        hovermode="x",
        hoverlabel=dict(
            namelength=-1,
            bordercolor="rgba(0,0,0,0)",
            font=dict(
                family="Roboto",
                color="#ECEFF1"
            )
        ),
        modebar={
            'bgcolor': 'rgba(0,0,0,0)',
            'color': '#CFD8DC',
            'activecolor': 'rgba(44, 62, 80, 0.8)',
        },
        yaxis=dict(
            title='Temperature (°C)',
            range=[-40, 120],
            dtick=20,
        ),
        yaxis2=dict(
            title='Photodiode Voltage (mV)',
            overlaying='y',
            side='right',
            tickmode="sync",
            range=[0, 400],
            dtick=50,
        ),
        legend=dict(
            orientation='h',
            yanchor='top',
            xanchor='center',
            x=0.5
        ),
        font=dict(
            family="Roboto",
            color="#2C3E50"
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(236, 239, 241, 1)'
    )
    fig.update_xaxes(gridcolor='#CFD8DC', zerolinecolor='#CFD8DC')
    fig.update_yaxes(gridcolor='#CFD8DC', zerolinecolor='#CFD8DC')
    return fig


if __name__ == "__main__":
    ScientificPlot().show()

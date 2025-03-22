
import src.db as db 
import src.Util as Util
import src.get as Get

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.offsetbox import OffsetImage,AnnotationBbox
import seaborn as sns


class plot:
    '''
    The functions which plot
    '''
    def params(data):
        '''
        Defining the data for the different subplots and the main plot
        as well as the event colors and event shots
        args:
            data(dict):                 takes in data
        returns:
            kde_home,kde_ab,kde_ab(ax):    axis for the kdePlots
            targetPlot(ax):             axis for the targets by shooters plot
            typePlot(ax):               axis for the shot type per team plot
            tablePlt(ax):               axis for the table of the shots
            period(ax):                 axis for the targets by period plot
            color_shots(dict):          the colors for the different types of shots
            event_colors(dict):         the colors for the different types of shot targets
        '''

        fig = plt.figure(figsize=(8,10))
        gs= gridspec.GridSpec(3, 3, figure=fig)

        kde_home =  fig.add_subplot(gs[0, 0])
        kde_ab = fig.add_subplot(gs[0, 1])
        kde_away = fig.add_subplot(gs[0, 2])
        targetPlot=  fig.add_subplot(gs[2, 0])
        typePlot=  fig.add_subplot(gs[1, 2])
        tablePlt = fig.add_subplot(gs[1,0])
        period = fig.add_subplot(gs[2,2])

        cmap = plt.get_cmap('tab20c')
        event_colors = {'goal':cmap(1%20), 'on goal':cmap(3%20),'blocked':cmap(5%20),
                'teammate-blocked':cmap(7%20),'miss':cmap(9%20),'metal':cmap(11%20)}
        color_shots={'snap':'tab:red','wrist':'tab:blue','slap':'tab:green','tip-in':'tab:cyan','backhand':'tab:orange','poke':'tab:purple',
              'deflected':'tab:olive','wrap-around':'tab:pink','bat':'tab:brown'}
        return {'kde_home':kde_home,'kde_away':kde_away,'kde_ab':kde_ab,'targetPlot':targetPlot,'typePlot':typePlot,'tablePlt':tablePlt,'period':period,'event_colors':event_colors,'color_shots':color_shots,
                'fig':fig,'plt':plt}


    def kde_plots(data,kde_home,kde_ab,kde_away):
        '''
        Plotting the kernel density estimation of positions
        '''
        img_rink = plt.imread("./img/rink.png")
        extent=[-43,43, 0, 100]
        levels=7
        thresh=0.25
        fill=False

        kde_home.imshow(img_rink, extent=extent,aspect='auto', zorder=1)
        sns.kdeplot(data=data['data_home'],
            warn_singular=False,
            x="yPos",
            y="xPos",
            levels=levels,
            thresh=thresh,
            fill=fill,
            ax=kde_home,
            color='red',
            extent=extent)
        Util.do.configure_plot(kde_home, f"{data['team_home']}'s shotpositions", extent)

        kde_ab.imshow(img_rink, extent=extent,aspect='auto', zorder=1)
        sns.kdeplot(data=data['combined_data'],
            x="yPos",
            y="xPos",
            fill=fill,
            ax=kde_ab,
            levels=levels,
            thresh=thresh,
            hue='team',
            legend=False,
            extent=extent,
            warn_singular=False,
            palette={f"{data['id_home']}": 'red', f"{data['id_away']}": 'blue'})
        Util.do.configure_plot(kde_ab, f"{data['team_home']} vs. {data['team_away']} shotpositions", extent)

        kde_away.imshow(img_rink, extent=extent,aspect='auto', zorder=1)
        sns.kdeplot(data=data['data_away'],
            warn_singular=False,
            x="yPos",
            y="xPos",
            fill=fill,
            thresh=thresh,
            ax=kde_away,
            levels=levels,
            color='blue',
            extent=extent)
        Util.do.configure_plot(kde_away, f"{data['team_away']}'s shotpositions", extent)
    
    def target_plot(data,targetPlot,event_colors):
        '''
        Plotting, the shot target for the top 4 shooters per team
        '''
        x_pos = 0
        for entry in data['d_home']:
            bottom = 0
            for key in data['d_home'][entry].keys():
                targetPlot.bar(x_pos, data['d_home'][entry][key], bottom=bottom, color=event_colors.get(key), label=key)
                bottom += data['d_home'][entry][key]
            imagebox_pl = OffsetImage(Get.image.player_img(entry), zoom=0.05, resample=True)
            targetPlot.add_artist(AnnotationBbox(imagebox_pl, (x_pos, bottom + 0.75), frameon=False))
            x_pos += 1
        x_pos = 4
        for entry in data['d_away']:
            bottom = 0
            for key in data['d_away'][entry].keys():
                targetPlot.bar(x_pos, data['d_away'][entry][key], bottom=bottom, color=event_colors.get(key), label=key)
                bottom += data['d_away'][entry][key]
            imagebox_pl = OffsetImage(Get.image.player_img(entry), zoom=0.05, resample=True)
            targetPlot.add_artist(AnnotationBbox(imagebox_pl, (x_pos, bottom + 1), frameon=False))
            x_pos += 1
        maxVal=Util.calc.max_val(data['d_home'],data['d_away'])

        targetPlot.set_ylim(0, maxVal+4)
        targetPlot.set_xticks([0, 1, 2, 3, 4, 5, 6, 7])
        targetPlot.set_xticklabels([Get.data.player_name(x) for x in data['d_home'].keys()] + [Get.data.player_name(x) for x in data['d_away'].keys()], rotation=90)
        targetPlot.set_title("Shooters by target")


    def shot_types_plot(data,typePlot,color_shots):
        '''
        Plotting the different shot types for each team
        normalized to 100&
        '''
        bottom=0
        typePlot.set_xticks(ticks=[0,1],labels=[data['team_home'],data['team_away']])
        for elem in data['shot_types_home']:
            typePlot.bar(0,elem[1]/data['shot_sums_home'],bottom=bottom,color=color_shots.get(elem[0]))
            bottom+=elem[1]/data['shot_sums_home']
        bottom=0
        for elem in data['shot_types_away']:
            typePlot.bar(1,elem[1]/data['shot_sums_away'],bottom=bottom,color=color_shots.get(elem[0]))
            bottom+=elem[1]/data['shot_sums_away']
        handles, labels = [], []
        for shot_type, color in color_shots.items():
            handles.append(plt.Line2D([0], [0], color=color, lw=4, label=shot_type))
            labels.append(shot_type)
            typePlot.legend(handles, labels,loc='center left', bbox_to_anchor=(-1.25,0.5), ncols=1,fontsize='small')
        typePlot.set_title("Shots by Shottype")
    def table(data,tablePlt):

        img_table_a=OffsetImage(Get.image.team_img(data['id_home']),zoom=0.045,resample=True)
        img_table_b=OffsetImage(Get.image.team_img(data['id_away']),zoom=0.045,resample=True)
        annotation_a = AnnotationBbox(img_table_a, (0.09, 0.55), frameon=False)
        annotation_b = AnnotationBbox(img_table_b, (1 - 0.09, 0.55), frameon=False)
        tablePlt.add_artist(annotation_a)
        tablePlt.add_artist(annotation_b) 

        tablePlt.table(cellText=data['table_data'],edges='open',colWidths=[0.5,2.5,0.5],bbox=[0,0.125,1,0.5],cellLoc='center')

        tablePlt.set_ylim(0,0.8)
        tablePlt.axis('off')
        textstr="Made with SQL & Python\nThanks to the NHL API"
        tablePlt.text(1.2, -1, textstr, fontsize=10,verticalalignment='top')

    def targetByPeriod(data,period,event_colors):
        '''
        Plotting the shot targets by time period by absolute values
        '''
        bottom_a,bottom_b=[],[]

        for key in data['event_counts_home'].keys():
            y_pos = {"P1": 2, "P2": 1, "P3": 0}
            bottom=0
            for k in data['event_counts_home'][key].keys():
                period.barh(y_pos.get(key), -data['event_counts_home'][key][k], 
                            left=bottom, label=k, color=event_colors.get(k))
                bottom -= data['event_counts_home'][key][k]
            bottom_a.append(bottom) 
        max_a=abs(min(bottom_a))
        period.axvline()
        for key in data['event_counts_away'].keys():
            y_pos = {"P1": 2, "P2": 1, "P3": 0}
            bottom=0
            for k in data['event_counts_away'][key].keys():
                period.barh(y_pos.get(key), data['event_counts_away'][key][k], 
                        left=bottom, label=k, color=event_colors.get(k))
                bottom += data['event_counts_away'][key][k]  # Update the bottom value for the next segment
            bottom_b.append(bottom) 
        max_b=abs(max(bottom_b))
        max_total=max(max_a,max_b)

        unique_labels = {}
        for elem in db.query.targetByPeriod(data['id_home'],data['gameId']) + db.query.targetByPeriod(data['id_away'],data['gameId']):
            if elem[2] not in unique_labels: unique_labels[elem[2]] = event_colors.get(elem[2])


        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))  # Remove duplicate labels
        period.legend(by_label.values(), by_label.keys(), title="Events",loc='lower left',bbox_to_anchor=(-1.25,0.3))
        period.set_xticks([-(max_total/2),max_total/2])
        period.set_xticklabels([data['team_home'],data['team_away']])
        period.get_xaxis().set_visible(True)
        period.set_title("Shots by Reg. period")
        period.set_xlim(-max_total, max_total) 
        period.set_yticks([2, 1,0], labels=["1st", "2nd", "3rd"])


    def final(data):
        '''
        putting all the subplots together into a single fig
        '''
        param=plot.params(data)
        plot.kde_plots(data,param['kde_home'],param['kde_ab'],param['kde_away'])
        plot.target_plot(data,param['targetPlot'],param['event_colors'])
        plot.shot_types_plot(data,param['typePlot'],param['color_shots'])
        plot.targetByPeriod(data,param['period'],param['event_colors'])
        plot.table(data,param['tablePlt'])
        title=f"{data['team_name_home']} vs {data['team_name_away']} Shot overview\n{data['date']} - {data['place']}"
        param['fig'].suptitle(title, fontsize=16)
        plt.savefig(f'./img/{data['gameId']}.png',dpi=300)
        plt.show()



function title (mode) {
    if (mode == 'mp') {
        return 'Multiplayer '
    } else if (mode == 'wz') {
        return 'Warzone '
    } else if (mode == 'cw') {
        return 'Cold war '
    }
}
function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}
function chart (duration) {
    var chart_data = window.location.href+"api/chart/"+duration+"/";
    var get_request = new XMLHttpRequest();
    get_request.onreadystatechange = function(){
        if (get_request.readyState == 4  ){
            var chart_json = JSON.parse(get_request.responseText);
            var border = [
               'rgba(255, 99, 132, 1)',
               'rgba(54, 162, 235, 1)',
               'rgba(255, 206, 86, 1)',
               'rgba(75, 192, 192, 1)',
               'rgba(153, 102, 255, 1)',
               'rgba(255, 159, 64, 1)',
               'rgba(22, 212, 203, 1)'
            ]
            var background = [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(153, 102, 255, 0.2)',
                'rgba(255, 159, 64, 0.2)',
                'rgba(22, 212, 203, 0.2)'
            ]
            var config = {
               responsive: true,
               maintainAspectRatio: false,
               scales: {
                   yAxes: [{
                       ticks: {
                           beginAtZero:true
                        }
                    }]
                }
            }
            var games = {}
            if (duration == 'week') {
                document.getElementById('chart').innerHTML = ''+
                '<ul class="nav nav-tabs flex" role="tablist">'+
                    '<li class="nav-item"><a class="nav-link active" href="#chart_week" data-bs-toggle="tab" role="tab">Week</a></li>'+
                    '<li class="nav-item"><a class="nav-link" href="#chart_lifetime" onclick="chart(&#039;lifetime&#039;); this.onclick=null;" data-bs-toggle="tab" role="tab">Lifetime</a></li>'+
                '</ul>'+
                '<div class="tab-content">'+
                    '<div class="tab-pane active" id="chart_week" role="tabpanel"></div>'+
                    '<div class="tab-pane" id="chart_lifetime" role="tabpanel"></div>'+
                '</div>';
                }
            for (mode in chart_json) {
                games[mode] = []
                document.getElementById('chart_'+duration).innerHTML += ''+
                '<h4 class="tab-title"><a href="'+window.location.href+'api/chart/'+duration+'/" target="_blank">'+title(mode)+'</a></h4>'+
                '<div class="chart">'+
                    '<canvas id="chart_'+duration+'_'+mode+'"></canvas>'+
                '</div>';
            }
            for (mode in chart_json) {
                for (user in chart_json[mode]['players']){
                    gamedata = {
                        label: user,
                        data: chart_json[mode]['players'][user],
                        backgroundColor: background,
                        borderColor: border,
                        borderWidth: 1
                    }
                    games[mode].push(gamedata)
                }
                var id_chart = document.getElementById('chart_'+duration+'_'+mode).getContext('2d');
                var chart = new Chart(id_chart, {
                    type: 'line',
                    data: {
                        labels: chart_json[mode]['dates'],
                        datasets: games[mode]
                    },
                   options: config
                });
            }
        }
    }
    get_request.open("GET", chart_data, true);
    get_request.send();
}

function get ( mode, many, user, nick, stats ) {
    var user_url = user.replace("#", "%23");
    if (mode == 'wz' && stats == '') {
        var colName = 'Place'
        var col1 = 'username'
        var col2 = 'teamPlacement'
        var col3 = 'totalXp'
        if (user != 'all') {
            shown_user_page ()
        } else {
            shown_page ()
        }
        table ()
    } else if (mode == 'mp' && stats == '') {
        var colName = 'Result'
        var col1 = 'username'
        var col2 = 'result'
        var col3 = 'totalXp'
        if (user != 'all') {
            shown_user_page ()
        } else {
            shown_page ()
        }
        table ()
    } else if (mode == 'cw' && stats == '') {
        var colName = 'Result'
        var col1 = 'user'
        var col2 = 'result'
        var col3 = 'xpAtEnd'
        if (user != 'all') {
            shown_user_page ()
        } else {
            shown_page ()
        }
        table ()
    } else if (mode == 'wz' && stats == 'lifetime') {
        var col = "DistanceTraveled"
        table_all ()
    } else if (mode == 'mp' && stats == 'lifetime') {
        var col = "Accuracy"
        table_all ()
    } else if (mode == 'cw' && stats == 'lifetime') {
        var col = "Accuracy"
        table_all ()
    }
    if (stats == 'stats') {
        var users_data = window.location.href+'api/'+mode+'/stats/1/'+user_url+'/-id/';
        var get_request = new XMLHttpRequest();
        get_request.onreadystatechange = function(){
            if (get_request.readyState == 4  ){
                var user_json = JSON.parse(get_request.responseText);
                document.getElementById("stats_"+mode+nick).innerHTML = '<h5><a href="'+window.location.href+'api/'+mode+'/stats/1/'+user_url+'/-id/" target="_blank">Summary stats</a> for last 20 matches:</h5>'+
                show_stats(user_json.data[0].summary_stats);
                document.getElementById("time_"+mode+nick).innerHTML = 'All time Stats on ['+new Date(user_json.data[0].time_all_summary_stats).toLocaleString('en-GB')+']';
                document.getElementById("stats_all_"+mode+nick).innerHTML = show_stats(user_json.data[0].all_summary_stats);
                if (mode == 'mp') {
                    document.getElementById("add_stats_all_"+mode+nick).innerHTML = '<h5>Additional stats:</h5>'+
                    show_stats(user_json.data[0].additional_all_stats);
                }
            }
       }
       get_request.open("GET", users_data, true);
       get_request.send();
    }
    function shown_user_page () {
        document.getElementById('page_'+mode+'_'+nick).innerHTML = ''+
        '<ul class="nav nav-tabs flex" role="tablist">'+
            '<li class="nav-item"><a class="nav-link active" href="#table_'+mode+'_'+nick+'" data-bs-toggle="tab" role="tab">Table</a></li>'+
            '<li class="nav-item"><a class="nav-link" href="#stats_'+mode+'_'+nick+'" onclick="get(&#039;'+mode+'&#039;, &#039;&#039;, &#039;'+user+'&#039;, &#039;'+nick+'&#039;, &#039;stats&#039;, &#039;-timestamp&#039;); this.onclick=null;" data-bs-toggle="tab" role="tab">Stats</a></li>'+
        '</ul>'+
        '<div class="tab-content">'+
            '<div class="tab-pane active" id="table_'+mode+'_'+nick+'" role="tabpanel">'+
                '<ul class="nav nav-tabs flex" role="tablist">'+
                    '<li class="nav-item"><a class="nav-link active" href="#last50_'+mode+'_'+nick+'" data-bs-toggle="tab" role="tab">Last 50</a></li>'+
                    '<li class="nav-item"><a class="nav-link" href="#lifetime_'+mode+'_'+nick+'" onclick="get(&#039;'+mode+'&#039;, &#039;all&#039;, &#039;'+user+'&#039;, &#039;'+nick+'&#039;, &#039;lifetime&#039;, &#039;-timestamp&#039;); this.onclick=null;" data-bs-toggle="tab" role="tab">Lifetime</a></li>'+
                '</ul>'+
                '<div class="tab-content">'+
                    '<div class="tab-pane active" id="last50_'+mode+'_'+nick+'" role="tabpanel"></div>'+
                    '<div class="tab-pane" id="lifetime_'+mode+'_'+nick+'" role="tabpanel"></div>'+
                '</div>'+
            '</div>'+
            '<div class="tab-pane" id="stats_'+mode+'_'+nick+'" role="tabpanel">'+
                '<p id="stats_'+mode+nick+'"></p>'+
                '<h5 id="time_'+mode+nick+'"></h5>'+
                '<p id="stats_all_'+mode+nick+'"></p>'+
                '<p id="add_stats_all_'+mode+nick+'"></p>'+
            '</div>'+
        '</div>';
    }
    function shown_page () {
        document.getElementById('page_'+mode).innerHTML = ''+
        '<ul class="nav nav-tabs flex" role="tablist">'+
            '<li class="nav-item"><a class="nav-link active" href="#'+mode+'_" data-bs-toggle="tab" role="tab">Table</a></li>'+
        '</ul>'+
        '<div class="tab-content">'+
            '<ul class="nav nav-tabs flex" role="tablist">'+
                '<li class="nav-item"><a class="nav-link active" href="#last50_'+mode+'_" data-bs-toggle="tab" role="tab">Last 50</a></li>'+
                '<li class="nav-item"><a class="nav-link" href="#lifetime_'+mode+'_" onclick="get(&#039;'+mode+'&#039;, &#039;all&#039;, &#039;'+user+'&#039;, &#039;'+nick+'&#039;, &#039;lifetime&#039;, &#039;-timestamp&#039;); this.onclick=null;" data-bs-toggle="tab" role="tab">Lifetime</a></li>'+
            '</ul>'+
            '<div class="tab-content">'+
                '<div class="tab-pane active" id="last50_'+mode+'_" role="tabpanel"></div>'+
                '<div class="tab-pane" id="lifetime_'+mode+'_" role="tabpanel"></div>'+
            '</div>'+
        '</div>';
    }
    function table () {
        document.getElementById('last50_'+mode+'_'+nick).innerHTML = ''+
        '<h4 class="tab-title"><a href="'+window.location.href+'api/'+mode+'/raw/'+many+'/'+user_url+'/-timestamp/" target="_blank">'+title(mode)+nick+' [50]</a></h4>'+
        '<table id="last50_table_'+mode+'_'+nick+'" style="width:100%" class="table table-hover">'+
            '<thead>'+
                '<tr>'+
                    '<th></th>'+
                    '<th>Played</th>'+
                    '<th>Player</th>'+
                    '<th>Duration</th>'+
                    '<th>Kills</th>'+
                    '<th>Deaths</th>'+
                    '<th>K/D</th>'+
                    '<th>'+colName+'</th>'+
                    '<th>TotalXp</th>'+
                '</tr>'+
            '</thead>'+
        '</table>';

        var table = $('#last50_table_'+mode+'_'+nick).DataTable( {
            "ajax": {
            "method": "GET",
            "url": window.location.href+"api/"+mode+"/raw/"+many+"/"+user_url+"/-timestamp/",
            "dataType": "json",
            },
            "columns": [
                {
                  "className":      'details-control',
                  "orderable":      false,
                  "data":           null,
                  "defaultContent": ''
                },
                {"data": "timestamp", "render": function(data, type) {
                    return type === 'sort' ? data : new Date(data).toLocaleString('en-GB');
                }},
                { "data": col1, "render": function(data) {
                    if (mode == 'cw') {
                        return data.split('#')[0]
                    } else {
                        return data
                    }
                } },
                { "data": "duration" },
                { "data": "kills" },
                { "data": "deaths" },
                { "data": "kdRatio" },
                { "data": col2 },
                { "data": col3 },
            ],
            "order": [[1, 'desc']],
            "searching": false
        } );

        $('#last50_table_'+mode+'_'+nick+' tbody').on('click', 'td.details-control', function () {
            var tr = $(this).closest('tr');
            var row = table.row( tr );
            if ( row.child.isShown() ) {
                row.child.hide();
                tr.removeClass('shown');
            }
            else {
                row.child( show(row.data(), mode), 'table-container' ).show();
                tr.addClass('shown');
            }
            } );
    }
    function table_all () {
        document.getElementById('lifetime_'+mode+'_'+nick).innerHTML = ''+
        '<h4 class="tab-title"><a href="'+window.location.href+'api/'+mode+"/table/all/"+user_url+'/-timestamp/" target="_blank">'+title(mode)+nick+' [all]</a></h4>'+
        '<table id="lifetime_table_'+mode+'_'+nick+'" style="width:100%" class="table table-hover">'+
            '<thead>'+
                '<tr>'+
                    '<th>Played</th>'+
                    '<th>Player</th>'+
                    '<th>Kills</th>'+
                    '<th>Deaths</th>'+
                    '<th>K/D</th>'+
                    '<th>DamageDone</th>'+
                    '<th>LongesStreak</th>'+
                    '<th>Headshots</th>'+
                    '<th>'+col+'</th>'+
                    '<th>TotalXp</th>'+
                '</tr>'+
            '</thead>'+
        '</table>';

        var table = $('#lifetime_table_'+mode+'_'+nick).DataTable( {
            "ajax": {
            "method": "GET",
            "url": window.location.href+"api/"+mode+"/table/"+many+"/"+user_url+"/-timestamp/",
            "dataType": "json",
            },
            "columns": [
                { "data": "Played" },
                { "data": "Player" },
                { "data": "Kills" },
                { "data": "Deaths" },
                { "data": "K/D" },
                { "data": "DamageDone" },
                { "data": "LongesStreak" },
                { "data": "Headshots" },
                { "data": col },
                { "data": "TotalXp" },
            ],
            "order": [[0, 'desc']],
            "searching": false
        } );
    }

    function show ( d, mode ) {
        var html = '<img src="/media/'+mode+'_maps/'+ d.map.replace(/\s|'|-|_rm/g, '')+'.gif" alt="Avatar" class="table-image"><div class="table-center"><div class="grid-container-table">';
        if (mode == 'mp' || mode == 'wz') {
            count = 0
            var ldt = ['primaryWeapon', 'secondaryWeapon', 'tactical', 'lethal'];
            final_loadout_html = ''
            for (loadout in d['loadout']) {
                loadout_html = ''
                count += 1
                ldt.forEach(wpn);
                function wpn(weapon) {
                    var label = d['loadout'][loadout][weapon]['label']
                    if (label == null || label == "") {
                        label = d['loadout'][loadout][weapon]['name']
                    }
                    if (label != 'none') {
                        if (weapon == 'primaryWeapon' || weapon == 'secondaryWeapon') {
                            console.log(label.length)
                            if (label.length < 50) {
                                loadout_html += '<li><a title="'+d['loadout'][loadout][weapon]['name']+'">'+label+'</a><ul>'
                            } else {
                                loadout_html += '<li><a title="'+d['loadout'][loadout][weapon]['label']+'">'+d['loadout'][loadout][weapon]['name']+'</a><ul>'
                            }
                            attachments = ''
                            for (i = 0; i < 5; i++) {
                                if (d['loadout'][loadout][weapon]['attachments'][i]['name'] != null && d['loadout'][loadout][weapon]['attachments'][i]['name'] != 'none') {
                                    attachments += '<li><a>'+(i+1)+' '+d['loadout'][loadout][weapon]['attachments'][i]['name']+'</a></li>'
                                    }
                                }
                            if (attachments != '') {
                                loadout_html += '<li><a>Attachments</a><ul>'+attachments+'</ul></li>'
                                }
                            }
                            if (weapon == 'tactical' || weapon == 'lethal') {
                                loadout_html += '<li><a title="'+d['loadout'][loadout][weapon]['name']+'">'+label+'</a><ul>'
                            }
                        loadout_html += '</ul></li>'
                    }
                }
                function perks () {
                    perks_html = ''
                    obj_perks = ''
                    obj_extraPerks = ''
                    if (mode == 'mp') {
                        for (i = 0; i < 3; i++) {
                            perk = d['loadout'][loadout]['perks'][i]['label']
                            if (perk != 'null' && perk != null) {
                                obj_perks += '<li><a title="'+d['loadout'][loadout]['perks'][i]['name']+'">'+perk+'</a></li>'
                            }
                        }
                        for (i = 0; i < 3; i++) {
                            extraPerk = d['loadout'][loadout]['extraPerks'][i]['label']
                            if (extraPerk != null && extraPerk != 'null') {
                                obj_extraPerks += '<li><a title="'+d['loadout'][loadout]['extraPerks'][i]['name']+'">'+extraPerk+'</a></li>'
                            }
                        }
                    }
                    if (mode == 'wz') {
                        for (i = 0; i < 3; i++) {
                            perk = d['loadout'][loadout]['perks'][i]['name'].replace(/\s|specialty_/g, '')
                            if (perk != 'null' && perk != null) {
                                obj_perks += '<li><a>'+perk+'</a></li>'
                            }
                        }
                        for (i = 0; i < 3; i++) {
                            extraPerk = d['loadout'][loadout]['extraPerks'][i]['name'].replace(/\s|specialty_/g, '')
                            if (extraPerk != null && extraPerk != 'null') {
                                obj_extraPerks += '<li><a>'+extraPerk+'</a></li>'
                            }
                        }
                    }
                    if (obj_perks != '') {
                        if (obj_extraPerks != '') {
                            obj_perks += '<li><a>ExtraPerks</a><ul>'+obj_extraPerks+'</ul></li>'
                        }
                        perks_html += '<li><a>Perks</a><ul>'+obj_perks+'</ul></li>'
                    }
                    if (obj_perks == '') {
                        perks_html = ''
                    }
                    return perks_html
                }
                function killstreaks () {
                    if (mode == 'mp') {
                        return ''+
                        '<li><a>Killstreaks</a>'+
                            '<ul>'+
                                '<li><a>'+d['loadout'][loadout]['killstreaks'][0]['label']+'</a></li>'+
                                '<li><a>'+d['loadout'][loadout]['killstreaks'][1]['label']+'</a></li>'+
                                '<li><a>'+d['loadout'][loadout]['killstreaks'][2]['label']+'</a></li>'+
                            '</ul>'+
                        '</li>';
                    } else {
                        return ''
                    }
                }
                final_loadout_html += '<li><a>'+count+'</a><ul>'+loadout_html+perks()+killstreaks()+'</ul></li>'
            }
            function weapon_stats () {
                if (mode == 'mp') {
                    try {
                        obj_stats = ''
                        for (weapons in d['weaponStats']) {
                            if (weapons != 'none' && d['weaponStats'][weapons]['startingWeaponXp'] != 0) {
                                obj_stats += ''+
                                '<li><a>'+weapons+'</a>'+
                                    '<ul>'+
                                        '<li><a>Hits: '+d['weaponStats'][weapons]['hits']+'</a></li>'+
                                        '<li><a>Kills: '+d['weaponStats'][weapons]['kills']+'</a></li>'+
                                        '<li><a>Deaths: '+d['weaponStats'][weapons]['deaths']+'</a></li>'+
                                        '<li><a>Headshots: '+d['weaponStats'][weapons]['headshots']+'</a></li>'+
                                        '<li><a>Shots: '+d['weaponStats'][weapons]['shots']+'</a></li>'+
                                        '<li><a>Starting WeaponXp: '+d['weaponStats'][weapons]['startingWeaponXp']+'</a></li>'+
                                        '<li><a>XpEarned: '+d['weaponStats'][weapons]['xpEarned']+'</a></li>'+
                                    '</ul>'+
                                '</li>';
                                }
                            }
                        weapons_html = '<ul class="dropdown"><li><a>Weapon stats</a><ul>'+obj_stats+'</ul></li></ul>'
                        } catch (e) {
                            weapons_html = ''
                        }
                        if (obj_stats == '') {
                            weapons_html = ''
                        }
                    return weapons_html
                } else {
                    return ''
                }
            }
            html += '<ul class="dropdown"><li><a>Loadouts</a><ul>'+final_loadout_html+'</ul></li></ul>'+weapon_stats()
        }
        for (stats in d) {
            if (['id', 'user', 'username', 'uno', 'clantag', 'timestamp', 'duration', 'kills', 'deaths', 'kdRatio', 'result', 'place', 'totalXp', 'loadout', 'weaponStats'].includes(stats) || d[stats] == null || d[stats] == 0) {
                continue
            } else {
                try {
                    html += ''+
                    '<div class="grid-item-table">'+
                    capitalize(stats.replace(/objective|Br|Medal|ScoreSs/g, ""))+
                    ': '+d[stats]+'</div>';
                } catch (e) {
                    html += e
                }
            }
        }
        return html+'</div></div>';
        }

    function show_stats ( d ) {
        function getRandomColor() {
            var x = Math.floor(Math.random() * 256);
            var y = Math.floor(Math.random() * 256);
            var z = Math.floor(Math.random() * 256);
            var bgColor = "rgb(" + x + "," + y + "," + z + "," + 0.1 + ")";
            return bgColor;
            }
        function fixed(number) {
            if ( number % 1 !== 0 ) {
                number = number.toFixed(2);
              }
              return number
        }
        var html = '<div class="grid-container">'
        for (stats in d) {
            if (stats == 'title') {
                continue
            } else {
                try {
                    html += ''+
                            '<div class="grid-item" style="background-color: '+getRandomColor()+';">'+
                                capitalize(stats.replace(/objective|Br|Medal|Score|Ss/g, "").replace(/([A-Z])/g, ' $1'))+': '+
                                fixed(d[stats])+
                            '</div>';
                        } catch (e) {
                            html += e
                }
            }
        }
        return html+'</div>'
        }
}

Controller = new function () {
    this.days = [];
    this.events = [];
    this.saveid = 0;
    this.dirty = false;

    this.init = () => {
        $('#settings-save').on('click', Controller.save);                   // 手动保存
        setTimeout(setInterval, 180000, Controller.try_auto_save, 180000);  // 每3分钟自动保存一次。
        $(window).unload(Controller.save);                                  // 关闭网站时自动保存
        Controller.setCloseEvent(300000);                                   // 标签页失去焦点的时候自动保存一次，冷却时间5分钟、
    };

    this.initFromDOM = () => {
        this.days = [];
        this.events = [];
        let DOMs = $('#t-div').children();
        let maxid = 0;
        for(let i = 0; i < DOMs.length; i++) {
            dom = $(DOMs[i]);
            if (dom.prop('id') && parseInt(dom.prop('id'))){
                maxid = Math.max(maxid,parseInt(dom.prop('id')));
            }
        }
        this._id = maxid;   // id从最大元素id+1开始标起
        let lastday; // 临时存一下day
        for (let i = 0; i < DOMs.length; i++) {
            dom = $(DOMs[i]);
            if (dom.hasClass('t-verbar')) {
                // continue;
            } else if (dom.hasClass('t-event-day')) {
                let day = new Day(
                    /*Date*/dom.attr('date'),
                    /*DateStr*/dom.find('.t-e-right-day')[0].innerHTML,
                    /*Id*/dom.prop('id')?parseInt(dom.prop('id')):0
                );
                this.days.push(day);
                lastday = day;
                dom.prop('id', day.id);
                //  console.log('Created day.');
                //  console.log(day);
            } else if (dom.hasClass('t-event')) {
                // let left on yourself.
                if (!lastday) {
                    console.log('Unparented event found.' + dom);
                    continue;
                }
                let hasdesc = dom.find('.event-descript').length > 0 && (/\S/g).test(dom.find('.event-descript')[0].innerHTML);
                let desc = hasdesc ? dom.find('.event-descript')[0].innerHTML.replace(/\n +/g, '') : null;
                let event = new Event(
                    /*Name*/dom.find('.event-title')[0].innerHTML,
                    /*HasDesc*/hasdesc,
                    /*canEdit*/true,
                    /*Desc*/desc,
                    /*Time*/dom.find('.t-e-left-event')[0].innerHTML,
                    /*Id*/dom.prop('id')?parseInt(dom.prop('id')):0
                );
                event.day = lastday;
                this.events.push(event);
                lastday.events.push(event);
                dom.prop('id', event.id);
                //  console.log('Created event.');
                //  console.log(event);
            } else if (dom.hasClass('t-plan')){
                lastday.task = dom.find('.t-plan-div')[0].innerHTML;
            } else {
                console.log('有什么奇怪的东西混进去了。');
            }
        }
    };

    this.createDay = () => {
        // get last day which has a date
        let lastdate = null;
        for(let i = 0; i<this.days.length; i--){
            let day = this.days[i];
            if(day.date._str);
            else {
                lastdate = day.date._date;break;
            }
        }
        if(!lastdate) lastdate = new MyDate(new Date());
        else{
            lastdate = new Date(lastdate.getTime() + 24*60*60*1000);
        }

        // create day
        let day = new Day(lastdate);

        this.days.splice(0, 0, day);
    };

    this.createEvent = obj => {
        let dayid = $(obj).closest('.t-event-day').prop('id');
        //console.log(dayid);
        let day = this.days.find(value => value.id == dayid);
        //console.log(day);
        // create event
        let event = new Event('', true, true, '', '');
        day.addEvent(event);
        this.events.push(event);
    };

    this.createDescript = obj => {
        alert('此功能还没做');
    };

    this.createTask = obj => {
        let dayid = $(obj).closest('.t-event-day').prop('id');
        //console.log(dayid);
        let day = this.days.find(value => value.id == dayid);
        //console.log(day);
        // create event
        day.addTask();
    };

    this.deleteTask = obj => {
        let dayid = $(obj).closest('.t-event-day').prop('id');
        //console.log(dayid);
        let day = this.days.find(value => value.id == dayid);
        //console.log(day);
        // create event
        day.delTask();
    };

    this.createEventFromEvent = obj => {
        this.initFromDOM();
        let eventid = $(obj).prop('id');
        let day = this.events.find(val => val.id == eventid).day;
        let event = new Event('', true, true, '', '');
        this.events.push(event);
        for (let i = 0; i < day.events.length; i++) {
            if (day.events[i].id == eventid) {
                day.events.splice(i + 1, 0, event);
                event.day = day;
                break;
            }
        }
        this.updateDOM();
        $('#' + event.id).find('.event-title').focus();
        this._last_input = Date.now();
    };

    this.deleteEvent = obj => {
        let eventid = $(obj).closest('.t-event').prop('id');
        let event = this.events.find(val => val.id == eventid);
        let day = event.day;
        this.events = this.events.filter(val => val.id != eventid);
        day.events = day.events.filter(val => val.id != eventid);
    };

    this.deleteDay = obj => {
        if (!confirm('是否删除此天的所有内容？！此操作难以恢复。')) return;
        let dayid = $(obj).closest('.t-event-day').prop('id');
        //console.log(dayid);
        this.days = this.days.filter(val => val.id != dayid);
    };

    this.addDescription = obj => {
        let eventid = $(obj).closest('.t-event').prop('id');
        let event = this.events.find(val => val.id == eventid);
        event.hasDesc = true;
    };

    this.updateAll = () => {
        for (let i = 0; i < this.days.length; i++) {
            this.days[i].update();
        }
    };

    this.updateDOM = () => {
        const getCaretPosition = function (element) {
            var caretOffset = 0;
            var doc = element.ownerDocument || element.document;
            var win = doc.defaultView || doc.parentWindow;
            var sel;
            if (typeof win.getSelection != "undefined") {//谷歌、火狐
            sel = win.getSelection();
            if (sel.rangeCount > 0) {//选中的区域
              var range = win.getSelection().getRangeAt(0);
              var preCaretRange = range.cloneRange();//克隆一个选中区域
              preCaretRange.selectNodeContents(element);//设置选中区域的节点内容为当前节点
              preCaretRange.setEnd(range.endContainer, range.endOffset);  //重置选中区域的结束位置
              caretOffset = preCaretRange.toString().length;
            }
            } else if ((sel = doc.selection) && sel.type !== "Control") {//IE
            var textRange = sel.createRange();
            var preCaretTextRange = doc.body.createTextRange();
            preCaretTextRange.moveToElementText(element);
            preCaretTextRange.setEndPoint("EndToEnd", textRange);
            caretOffset = preCaretTextRange.text.length;
            }
            return caretOffset;
        };//获取当前光标位置
        const setCaretPosition = function (element, pos) {
            var range, selection;
            if (document.createRange)//Firefox, Chrome, Opera, Safari, IE 9+
            {
            range = document.createRange();//创建一个选中区域
            range.selectNodeContents(element);//选中节点的内容
            if(element.innerHTML.length > 0) {
              range.setStart(element.childNodes[0], pos); //设置光标起始为指定位置
            }
            range.collapse(true);       //设置选中区域为一个点
            selection = window.getSelection();//获取当前选中区域
            selection.removeAllRanges();//移出所有的选中范围
            selection.addRange(range);//添加新建的范围
            }
            else if (document.selection)//IE 8 and lower
            {
            range = document.body.createTextRange();//Create a range (a range is a like the selection but invisible)
            range.moveToElementText(element);//Select the entire contents of the element with the range
            range.collapse(false);//collapse the range to the end point. false means collapse to end rather than the start
            range.select();//Select the range (make it the visible selection
            }
        };//设置光标位置
        let caretDiv = $(document.activeElement).prop('id');
        let caretPos = getCaretPosition(document.activeElement);

        let alldiv = '<div class="t-verbar"></div>';
        for (let i = 0; i < this.days.length; i++) {
            let day = this.days[i];
            // day.update();
            // create div
            let daydiv =
                '<div class="t-event t-event-day" id="' + day.id + '" date="'+ day.date._date +'">' +
                '<div class="t-e-left">' +
                '<div class="t-e-left-day">' +
                '</div>' +
                '</div>' +
                '<div class="t-e-ball ball-day" onclick="return Menu.show(this);"></div>' +
                '<div class="t-menu dropdown-menu">' +
                '<span class="dropdown-item" onclick="Controller.initFromDOM();Controller.createDay();Controller.updateDOM();">Add Day</span>' +
                '<span class="dropdown-item" onclick="Controller.initFromDOM();Controller.deleteDay(this);Controller.updateDOM();">Delete Day</span>' +
                '<span class="dropdown-item" onclick="Controller.initFromDOM();Controller.createEvent(this);Controller.updateDOM();">Add Event</span>' +
                '<span class="dropdown-item" onclick="Controller.initFromDOM();Controller.createDescript(this);Controller.updateDOM();">Add Description</span>' +
                '<span class="dropdown-item" onclick="Controller.initFromDOM();Controller.createTask(this);Controller.updateDOM();">Show Task</span>' +
                '<span class="dropdown-item" onclick="Controller.initFromDOM();Controller.deleteTask(this);Controller.updateDOM();">Hide Task</span>' +
                '</div>' +
                '<div class="t-e-right">' +
                '<div class="t-e-right-day" contenteditable="true" id="' + day.id + '_day">' +
                day.date.show() +
                '</div>' +
                '</div>' +
                '</div>';
            if(day.task){
                daydiv += "<div class=\"t-plan\" id=\""+ day.id +"_task\"><div class=\"t-plan-div\">" + day.task + "</div></div>";
            }
            for (let i = 0; i < day.events.length; i++) {
                let event = day.events[i];
                let eventdiv =
                    '<div class="t-event" id="' + event.id + '">' +
                    '<div class="t-e-left">' +
                    '<div class="t-e-left-event" ' + (event.canEdit ? 'contenteditable="true"' : '') + ' id="' + event.id + '_event">' +
                    event.time +
                    '</div>' +
                    '</div>' +
                    '<div class="t-e-ball ball-event" onclick="return Menu.show(this);"></div>' +
                    '<div class="t-menu dropdown-menu">' +
                    '<span class="dropdown-item" onclick="Controller.initFromDOM();Controller.addDescription(this);Controller.updateDOM();">Add Description</span>' +
                    '<span class="dropdown-item" onclick="Controller.initFromDOM();Controller.deleteEvent(this);Controller.updateDOM();">Delete Event</span>' +
                    '</div>' +
                    '<div class="t-e-right">' +
                    '<div class="t-e-right-event">' +
                    '<div class="event-title"' + (event.canEdit ? 'contenteditable="true"' : '') + ' id="' + event.id + '_title">' +
                    event.name +
                    '</div>' +
                    (
                        !event.hasDesc ? '' :
                            '<div class="event-descript"' + (event.canEdit ? 'contenteditable="true"' : '') + ' id="' + event.id + '_des">' +
                            event.desc +
                            '</div>'
                    ) +
                    '</div>' +
                    '</div>' +
                    '</div>';
                daydiv += eventdiv;
            }
            alldiv += daydiv;
        }
        $('#t-div').html(alldiv);

        for (let i = 0; i < this.events.length; i++) {
            let eventid = this.events[i].id;

            // 在事件标题中按回车，添加事件，并修改焦点
            $('#' + eventid).find('.event-title').keypress(function (event) {
                var keynum = (event.keyCode ? event.keyCode : event.which);
                if (keynum === 13) {
                    // alert('You pressed a "Enter" key in somewhere');
                    //console.log(this);
                    Controller.createEventFromEvent($('#' + eventid));
                    return false;
                }
                else
                    Controller._last_input = Date.now();
            });
            // 写description时Ctrl+Enter也可以添加事件
            $('#' + eventid).find('.event-descript').keypress(function (event) {
                // console.log(event);
                var keynum = (event.keyCode ? event.keyCode : event.which);
                if ((keynum === 10 || keynum === 13) && event.ctrlKey) {
                    // Windows上Ctrl+Enter的键码是10；Mac、Linux等上是13。
                    console.log('You pressed a "Ctrl+Enter" key in somewhere');
                    //console.log(this);
                    Controller.createEventFromEvent($('#' + eventid));
                    return false;
                }
                else
                    Controller._last_input = Date.now();
            });
        }

        this.dirty = false;
        $('.event-title, .event-descript, .t-e-left-event').on('change blur', function (event){
            Controller.dirty = true;
        });

        $('.t-plan-text').on('keypress',function (event) {
                Controller._last_input = Date.now();
                var keynum = (event.keyCode ? event.keyCode : event.which);
                if (keynum === 13) {

                    let dayid = parseInt($(this).closest('.t-plan').prop('id'));
                    //console.log(dayid);
                    Controller.initFromDOM();
                    let day = Controller.days.find(value => value.id == dayid);

                    day.task += '<div class="t-plan-line"><div class="t-plan-check"><div class="inner"></div></div><div class="t-plan-text" contenteditable=true>Example task.</div></div>';
                    console.log(day);

                    Controller.updateAll();
                    Controller.updateDOM();

                    Controller.dirty = true;
                    return false;
                }

                Controller.dirty = true;
            });

        if(caretDiv){
            setCaretPosition(document.getElementById(caretDiv), caretPos);
        }
    };

    this._last_input = Date.now();
    this._last_save = Date.now();
    this.save = (type='auto') => {
        // 未修改
        if(!this.dirty) {
            if(type !== 'auto'){
                alert('上次保存后未修改！')
            }
            return;
        }
        // 无保存权限的页面
        if(!Controller.saveid) return;
        // 保存
        Controller.initFromDOM();
        Controller.updateAll();
        Controller.updateDOM();
        var formData = new FormData();
        formData.append("content", $('#t-div').html());
        formData.append("saveid", Controller.saveid);
        formData.append("action", "save");
        if(type === 'auto') {
            formData.append("autosave", "1");
        }
        $.ajax({
            url: '/life/__action',
            type: 'post',
            data: formData,
            processData: false,
            contentType: false,
            success: function (msg) {
                if(type === 'auto'){
                    console.log('自动保存 '+Date(Date.now()));
                    console.log(msg);
                }else {
                    alert(msg);
                }
            }
        });
        this._last_save = Date.now();
        // return false;
    };
    this.try_auto_save = () => {
        // 未修改
        if(!this.dirty) return;
        // 此函数用于自动保存
        // 由于各种原因，我们不希望用户正在输入的过程中执行保存操作。
        // 因此当自动保存事件触发时，如果用户正在输入，则执行CSMA/CD避让算法。
        if(Date.now() - this._last_save < 30000){
            // 30秒内已经保存过一次啦！直接返回
            return;
        }
        if(Date.now() - this._last_input < 10000){
            // 10秒内刚进行过键盘输入，认为是正在打字，过一会再来试试。
            setTimeout(this.try_auto_save, 3000)
        }else{
            this.save();
        }
    };

    this._visibility_save = true;
    this.setCloseEvent = lag => {
        var hiddenProperty = 'hidden' in document ? 'hidden' :'webkitHidden' in document ? 'webkitHidden' : 'mozHidden' in document ? 'mozHidden' : null;
        var visibilityChangeEvent = hiddenProperty.replace(/hidden/i, 'visibilitychange');
        document.addEventListener(visibilityChangeEvent, event => {
            if(document[hiddenProperty]) {
                if(this._visibility_save) {
                    this.save();
                    this._visibility_save = false;
                    setTimeout(() => {
                        this._visibility_save = true;
                    }, lag);
                }
            }
        });
    };

    this._id = 100;
    this.getid = () => {
        return ++this._id;
    };
}();

function Day(date, datestr, id=0) {
    this.id = id?id:Controller.getid();
    this.date = new MyDate(date, datestr);
    this.desc = "";
    this.task = "";
    this.events = [];
    this.update = () => {
        this.events.sort((a, b) => a.compareTime(b));
    };

    this.addTask = () => {
        console.log('added');
        this.task =
            "<div class=\"t-plan-title\">Tasks</div>" +
            "<div class=\"t-plan-line\">" +
                "<div class=\"t-plan-check\">" +
                "<div class=\"inner\"></div>" +
                "</div>" +
                "<div class='t-plan-text' contenteditable=true>Example task.</div>" +
            "</div>";
        this.taskid = Controller.getid();
    };

    this.delTask = () => {
        this._task = this.task;
        this.task = "";
    };

    this.addEvent = event => {
        this.events.push(event);
        event.day = this;
        this.update();
    };

    this.removeEvent = eventid => {
        console.log('Removed event: ');
        console.log(event);
        //this.events.remove(event);
        this.events.find(val => val.id == eventid).day = null;
        this.events = this.events.filter(val => val.id != eventid);
        this.update();
    };
}

function Event(name, hasdesc, canedit, desc, time, id=0) {
    this.id = id? id :Controller.getid();
    this.name = name;
    this.hasDesc = hasdesc;
    this.canEdit = true;
    this.desc = desc;
    this.time = time;
    this.day = null;
    this.compareTime = b => {
        /*
            比较两个Event的时间
            时间格式：类似于 7:30 pm - 12:30 am
            匹配出其中的第一个时间与第二个时间（如果有），然后依次比较。
         */
        let regex = /[0|1]?[0-9]:[0-9]{2} [ap]m/g;
        let cal = time => {
            let t = 0, s = 0, i = 0;
            for (; time[i] !== ':'; i++) {
                t = t * 10;
                t += parseInt(time[i]);
            }
            t *= 60;
            for (i++; time[i] !== ' '; i++) {
                s = s * 10;
                s += parseInt(time[i]);
            }
            t += s;
            while (time[i] === ' ') i++;
            if (time[i] === 'p') t += 720;
            else if (time[i] === 'a') i++;
            else t = 99999;
            //    console.log('Time: ' + time + ', Result: ' + t);
            return t;
        };
        //console.log(this.time);
        //console.log(this.time.match(regex));
        let a_times = this.time.match(regex);
        let b_times = b.time.match(regex);
        if (!a_times) return 1;
        else if (!b_times) return -1;
        a_times = a_times.map(cal);
        b_times = b_times.map(cal);
        if (a_times[0] !== b_times[0]) return a_times[0] - b_times[0];
        else if (a_times.length === 1) return -1;
        else if (b_times.length === 1) return 1;
        return a_times[1] - b_times[1];
    };
}

Settings = new function (){
    this.initAll = () => {
        setTimeout(()=>this.initRollback(), 1200); // saveid will be set after 1000 milliseconds
    };

    this.initRollback = () => {
        if(!Controller.saveid) return;
        // 保存
        var formData = new FormData();
        formData.append("saveid", Controller.saveid);
        formData.append("action", "rollback");
        $.ajax({
            url: '/life/__action',
            type: 'post',
            data: formData,
            processData: false,
            contentType: false,
            async: true,
            success: function (msg) {
                msg = JSON.parse(msg);
                if(msg.success == 'false'){
                    console.log(msg.msg)
                }
                else{
                    content = '<ul class="list-group t-settings-ul">';
                    for(let i=0;i<parseInt(msg['length']);i++) {
                        content += '<li class="list-group-item t-settings-li" ' +
                        'onclick="document.location=document.location.toString().split(\'?\')[0]+\'?use_saved=' + msg[''+i] + '\'"' +
                            '>' + msg['' + i] + '</li>';
                    }
                    content += '</ul>';
                    $('#settings-right-rollback').html(content);
                }
            }
        });
    }
}();

Menu = new function() {
    this.buttonClicked = false;

    this.init = () => {
        $('body').on('click', event => {
            // 左边空白处点击时关闭打开的菜单
            setTimeout(() => {
                if (Menu.buttonClicked) {
                    Menu.buttonClicked = false;
                    return;
                }
                $('.show').removeClass('show');
            }, 50);
        });

        $('.t-verbar').css("height",($('#t-div').height()-10)+"px")
    };

    this.show = obj => {
        this.buttonClicked = true;
        let a = $(obj).next();
        if (a.hasClass('show'))
            a.removeClass('show');
        else
            a.addClass('show');
        return false;
    };
}();

function MyDate(obj, str){
    this._date = obj? new Date(obj): new Date("ybd");
    if(!this._date.getTime()){
        this._str = str;
    }
    else{
        this._str = null;
    }

    this.show = () => {
        if(this._str){
            return this._str;
        }
        const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sept','Oct','Nov','Dec'];
        const weekday = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
        return months[this._date.getMonth()]+' '+
            this._date.getDate()+
            '<sup>'+
            ((this._date.getDate()===1||this._date.getDate()===21||this._date.getDate()===31)?'st':
                (this._date.getDate()===2||this._date.getDate()===22)?'nd':
                    (this._date.getDate()===3||this._date.getDate()===23)?'rd':
                        'th')
            +'</sup> &nbsp;&nbsp;'+
            weekday[this._date.getDay()]
    };
}

$(() => {
    Controller.init();
    Controller.initFromDOM();
    Controller.updateAll();
    Controller.updateDOM();

    Menu.init();

    Settings.initAll();
});
Controller = new function () {
    this.days = [];
    this.events = [];
    this.saveid = 0;
    this.initFromDOM = () => {
        this.days = [];
        this.events = [];
        let DOMs = $('#t-div').children();
        let lastday; // 临时存一下day
        for (let i = 0; i < DOMs.length; i++) {
            dom = $(DOMs[i]);
            if (dom.hasClass('t-verbar')) {
                // continue;
            } else if (dom.hasClass('t-event-day')) {
                let day = new Day(
                    /*Date*/dom.find('.t-e-right-day')[0].innerHTML
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
                    /*Time*/dom.find('.t-e-left-event')[0].innerHTML
                );
                event.day = lastday;
                this.events.push(event);
                lastday.events.push(event);
                dom.prop('id', event.id);
                //  console.log('Created event.');
                //  console.log(event);
            } else {
                console.log('有什么奇怪的东西混进去了。');
            }
        }
    };
    this.createDay = () => {
        // create day
        let day = new Day('April 24<sup>th</sup>');
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
        let alldiv = '<div class="t-verbar"></div>';
        for (let i = 0; i < this.days.length; i++) {
            let day = this.days[i];
            // day.update();
            // create div
            let daydiv =
                '<div class="t-event t-event-day" id="' + day.id + '">' +
                '<div class="t-e-left">' +
                '<div class="t-e-left-day">' +
                '</div>' +
                '</div>' +
                '<div class="t-e-ball ball-day" onclick="return showMenu(this);"></div>' +
                '<div class="t-menu dropdown-menu">' +
                '<span class="dropdown-item" onclick="Controller.initFromDOM();Controller.createEvent(this);Controller.updateDOM();">Add Event</span>' +
                '<span class="dropdown-item" onclick="Controller.initFromDOM();Controller.createDay();Controller.updateDOM();">Add Day</span>' +
                '<span class="dropdown-item" onclick="Controller.initFromDOM();Controller.deleteDay(this);Controller.updateDOM();">Delete Day</span>' +
                '</div>' +
                '<div class="t-e-right">' +
                '<div class="t-e-right-day" contenteditable="true">' +
                day.date +
                '</div>' +
                '</div>' +
                '</div>';
            for (let i = 0; i < day.events.length; i++) {
                let event = day.events[i];
                let eventdiv =
                    '<div class="t-event" id="' + event.id + '">' +
                    '<div class="t-e-left">' +
                    '<div class="t-e-left-event" ' + (event.canEdit ? 'contenteditable="true"' : '') + '>' +
                    event.time +
                    '</div>' +
                    '</div>' +
                    '<div class="t-e-ball ball-event" onclick="return showMenu(this);"></div>' +
                    '<div class="t-menu dropdown-menu">' +
                    '<span class="dropdown-item" onclick="Controller.initFromDOM();Controller.deleteEvent(this);Controller.updateDOM();">Delete Event</span>' +
                    '<span class="dropdown-item" onclick="Controller.initFromDOM();Controller.addDescription(this);Controller.updateDOM();">Add Description</span>' +
                    '</div>' +
                    '<div class="t-e-right">' +
                    '<div class="t-e-right-event">' +
                    '<div class="event-title"' + (event.canEdit ? 'contenteditable="true"' : '') + '>' +
                    event.name +
                    '</div>' +
                    (
                        !event.hasDesc ? '' :
                            '<div class="event-descript"' + (event.canEdit ? 'contenteditable="true"' : '') + '>' +
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

            // 在事件标题中按回车，添加事件
            $('#' + eventid).find('.event-title').keypress(function (event) {
                var keynum = (event.keyCode ? event.keyCode : event.which);
                if (keynum == 13) {
                    // alert('You pressed a "Enter" key in somewhere');
                    //console.log(this);
                    Controller.createEventFromEvent($('#' + eventid));
                    return false;
                }
            });
        }
    };
    this._id = 100;
    this.getid = () => {
        return ++this._id;
    };
}();

function Day(date) {
    this.id = Controller.getid();
    this.date = date;
    this.events = [];
    this.update = () => {
        this.events.sort((a, b) => a.compareTime(b));
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

function Event(name, hasdesc, canedit, desc, time) {
    this.id = Controller.getid();
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


buttonClicked = false;
function showMenu(obj) {
    buttonClicked = true;
    let a = $(obj).next();
    if (a.hasClass('show'))
        a.removeClass('show');
    else
        a.addClass('show');
    return false;
}

$('body').on('click', event => {
    // 左边空白处点击时关闭打开的菜单
    setTimeout(()=>{
        if (buttonClicked){
            buttonClicked = false;
            return;
        }
        $('.show').removeClass('show');
    },50);
    return false;
});

$('#logo').on('click', event=>{
    // 保存
    Controller.initFromDOM();
    Controller.updateAll();
    Controller.updateDOM();
    var formData = new FormData();
    formData.append("content", $('#t-div').html());
    formData.append("saveid", Controller.saveid);
    $.ajax({
        url: '/savelife',
        type: 'post',
        data: formData,
        processData: false,
        contentType: false,
        success: function (msg) {
            alert(msg);
        }
    });
    return false;
});


$(() => {
    Controller.initFromDOM();
    Controller.updateAll();
    Controller.updateDOM();
});
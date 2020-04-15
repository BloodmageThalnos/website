const URL_ACTION = "/life/__action";
const AUTO_SAVE_INTERVAL = 3 * 1000;
const VERSION = '10002.01';

Static = new function() { // static functions
    // 获取当前div在其兄弟中的index
    this.getChildrenIndex = ele => { //IE
        if (ele.sourceIndex) return ele.sourceIndex - ele.parentNode.sourceIndex - 1;
        //other
        var i = 0;
        while (ele = ele.previousElementSibling) i++;
        return i;
    };
    //获取当前光标位置
    this.getCaretPosition = element => {
        var caretOffset = 0;
        var doc = element.ownerDocument || element.document;
        var win = doc.defaultView || doc.parentWindow;
        var sel;
        if (typeof win.getSelection !== "undefined") {//谷歌、火狐
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
    };
    //设置光标位置
    this.setCaretPosition = (element, pos) => {
        var range, selection;
        try {
            range = document.createRange();//创建一个选中区域
            range.selectNodeContents(element);//选中节点的内容
            if (element.innerHTML.length > 0) {
                range.setStart(element.childNodes[0], pos); //设置光标起始为指定位置
            }
            range.collapse(true);       //设置选中区域为一个点
            selection = window.getSelection();//获取当前选中区域
            selection.removeAllRanges();//移出所有的选中范围
            selection.addRange(range);//添加新建的范围
        }catch(err){}finally{}
    };
    //稳定排序，需下标为数字
    this.stable_sort = (arr, comp) => {
        for(let i in arr) arr[i]._ind = i;
        return arr.sort((a,b)=>{return comp(a,b)||(a._ind-b._ind);});
    };
}();

Controller = new function () {
    this.days = [];
    this.events = [];
    this.saveid = 0;
    this.customScript = "";

    this.dirty = false; // 界面是否被修改
    this.updatingDom = false; // 正在updateDom等
    this.init = () => {
        // 保存相关
        document.body.addEventListener("DOMCharacterDataModified",function(e){
            if(Controller.updatingDom)return;
            Controller.dirty = true;
        });
        _ldirty = false;
        setTimeout(setInterval, 10000, function(e){
            if(Controller.dirty){
                _ldirty = true;
                Controller.dirty = false;
            }else if(_ldirty){
                Controller.try_auto_save();
                _ldirty = false;
            }
        }, AUTO_SAVE_INTERVAL); // 如果发现内容是脏的，且X秒没有更新过了，就提交一次save。
        $('#settings-save').on('click', ()=>{Controller.save(false, true);}); // 手动保存。
        $(window).unload(function(e){
            if(Controller.dirty || _ldirty) Controller.save(true, false);
        }) // 关闭网站时，如果内容脏，强制保存。
        // Controller.onCloseEvent(60000); // 标签页失去焦点的时候自动保存，冷却时间1分钟。
    };

    this.initFromDOM = () => {
        if(!$('#version')[0]){ // remove later
            let h = $('#t-div').html();
            if(h.indexOf('class="t-timeline"')===-1) {
                h = '<div id="version" data-version="10001.00"></div><div class="t-timeline" id="t-timeline">' + h + '</div>';
                $('#t-div').html(h)
            }
            else{
                h = '<div id="version" data-version="' + VERSION + '"></div>' + h;
                $('#t-div').html(h);
            }
        }

        this.version = $('#version').attr('data-version');
        if(this.version === '10001.00'){
            console.log('Warning: Protected version.');
            return;
        }

        this.days = [];
        this.events = [];
        this.customScript = $('#custom').html()?$('#custom').html():"";
        let DOMs = $('#t-timeline').children();
        let maxid = 0;
        for(let i = 0; i < DOMs.length; i++) {
            dom = $(DOMs[i]);
            if (dom.prop('id') && parseInt(dom.prop('id'))){
                maxid = Math.max(maxid, parseInt(dom.prop('id')));
            }
        }
        for(let i = 0, d = $('#t-task-dynamic').children(); i < d.length; i++) {
            dom = $(d[i]);
            if (dom.prop('id') && parseInt(dom.prop('id'))){
                maxid = Math.max(maxid, parseInt(dom.prop('id')));
            }
        }
        this._id = maxid;   // id从最大元素id+1开始标起
        let lastday = null; // lastday表示最近的一个day（当前day）
        for(let i = 0; i < DOMs.length; i++) {
            let dom = $(DOMs[i]);
            if (dom.hasClass('t-event-day')) {
                let day = new Day(
                    /*Date*/dom.attr('date'),
                    /*DateStr*/dom.find('.t-e-right-day')[0].innerHTML,
                    /*Desc*/(dom.find('.t-e-right-day-desc').length?dom.find('.t-e-right-day-desc')[0].innerHTML:""),
                    /*Id*/(dom.prop('id')?parseInt(dom.prop('id')):0)
                );
                this.days.push(day);
                lastday = day;
            }
            else if (dom.hasClass('t-event')) {
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
            }
            else if (dom.hasClass('t-plan')){
                let task = new Task();
                let id = dom.prop('id');
                if(id && id.length > 5 && id[id.length-1]==='k') {
                    task.id = parseInt(id);
                } else {
                    console.log('Unexpected plan id: '+ id);
                    task.id = Controller.getid();
                }
                let lines_dom = dom.find('.t-plan-line');
                for(let i = 0; i<lines_dom.length; i++){
                    let line = $(lines_dom[i]).html();
                    let regex = /class=\"inner *(\S*?)\"><\/div/g; //从class name获取打勾打叉信息
                    let res = regex.exec(line);
                    let check = res?res[1]:"";
                    task.check.push(check);

                    regex = /class="t-plan-text" contenteditable="true">(.*)<\/div>/g;
                    res = regex.exec(line);
                    let content;
                    if(res!= null){
                        content = res[1];
                    }else{
                        content = "";
                    }
                    task.lines.push(content);
                }
                task.day = lastday;
                lastday.task = task;
            }
            else if (dom.hasClass('t-verbar')) {
            }
            else if(dom[0].id === "custom"){// custom script, we may have a check here.
            }
            else {
                console.log('Something unexcepted:\n'+dom[0].outerHTML);
            }
        }
        this.tasks = [];
        this.subtasks = [];
        DOMs = $('#t-task-dynamic').children();
        let last_task = null;
        for(let i = 0; i < DOMs.length; i++) {
            let dom = $(DOMs[i]);
            if (dom.hasClass('t-task-outer')){
                let task = TaskV2.fromHtml(dom);
                if(!task){
                    console.log('Something unexcepted:\n'+dom[0].outerHTML);
                    continue;
                }
                this.tasks.push(task);
                last_task = task;
            }
            else if(dom.hasClass('t-subtask-outer')){
                if(!last_task){
                    console.log('Found unparented subtask.\n');
                    continue;
                }
                let subtask = Subtask.fromHtml(dom);
                if(!subtask){
                    console.log('Something unexcepted:\n'+dom[0].outerHTML);
                    continue;
                }
                last_task.addSubtask(subtask);
                subtask.parent = last_task;
                this.subtasks.push(subtask);
            }
            else {
                console.log('Something unexcepted:\n'+dom[0].outerHTML);
            }
        }
        for(let i = 0; i < this.tasks.length; i++){
            this.tasks[i].checkStatus();
        }
    };

    this.createDay = () => {
        // get last day which has a date
        let lastdate = null;
        for(let i = 0; i<this.days.length; i++){
            let day = this.days[i];
            if(day.date._str) {  // day,date._str 非空表示date为手动输入的，而非日期。
            }
            else {
                lastdate = day.date._date;break;
            }
        }
        if(!lastdate) {
            lastdate = new Date(); // 当前日期（今天）
        }
        else{
            lastdate = new Date(lastdate.getTime() + 24*60*60*1000); // 上一个日期+1
        }

        let day = new Day(lastdate);
        day.addDesc();

        let event = new Event('', true, true, '', '');
        day.addEvent(event);
        this.events.push(event);

        this.days.splice(0, 0, day);

        Controller.dirty = true;
    };

    this.createEvent = obj => {
        let dayid = $(obj).closest('.t-event-day').prop('id');
        let day = this.days.find(value => value.id == dayid);

        let event = new Event('', true, true, '', '');
        day.addEvent(event);
        this.events.push(event);

        Controller.dirty = true;
    };

    this.createDescript = obj => {
        let dayid = $(obj).closest('.t-event-day').prop('id');
        let day = this.days.find(value => value.id == dayid);
        day.addDesc();

        Controller.dirty = true;
    };

    this.createTask = obj => {
        let dayid = $(obj).closest('.t-event-day').prop('id');
        let day = this.days.find(value => value.id == dayid);
        day.addTask();

        Controller.dirty = true;
    };

    this.editDate = obj => {
        let dayid = $(obj).closest('.t-event-day').prop('id');
        let day = this.days.find(value => value.id == dayid);
        day.date._str = day.date.show();
        day.date._date = null;

        Controller.dirty = true;
    };

    this.setDate = obj => {
        let dayid = $(obj).closest('.t-event-day').prop('id');
        let day = this.days.find(value => value.id == dayid);
        day.date._str = null;
        let datestr = prompt('请输入日期', new Date());
        day.date._date = new Date(datestr);

        Controller.dirty = true;
    };

    this.deleteTask = obj => {
        let dayid = $(obj).closest('.t-event-day').prop('id');
        let day = this.days.find(value => value.id == dayid);
        day.delTask();

        Controller.dirty = true;
    };

    this.createEventFromEvent = (obj, before=0) => {   // before=1表示在Event之前插入，否则在之后插入
        Controller.initFromDOM();
        let eventid = parseInt($(obj).prop('id'));
        let day = this.events.find(val => val.id === eventid).day;
        let event = new Event('', true, true, '', '');
        this.events.push(event);
        for (let i = 0; i < day.events.length; i++) {
            if (day.events[i].id === eventid) {
                day.events.splice(i + !before, 0, event);
                event.day = day;
                break;
            }
        }
        Controller.updateDOM();
        $('#' + event.id).find('.event-title').focus();

        Controller.dirty = true;
    };

    this.deleteEvent = obj => {
        let eventid = $(obj).closest('.t-event').prop('id');
        let event = this.events.find(val => val.id == eventid);
        let day = event.day;
        this.events = this.events.filter(val => val.id != eventid);
        day.events = day.events.filter(val => val.id != eventid);

        Controller.dirty = true;
    };

    this.deleteDay = obj => {
        if (!confirm('是否删除此天的所有内容？！此操作可能无法恢复。')) return;
        let dayid = $(obj).closest('.t-event-day').prop('id');
        this.days = this.days.filter(val => val.id != dayid);

        Controller.dirty = true;
    };

    this.addDescription = obj => {
        Controller.initFromDOM();

        let eventid = parseInt($(obj).closest('.t-event').prop('id'));
        let event = this.events.find(val => val.id === eventid);
        event.hasDesc = true;
        event.desc = "";

        Controller.updateDOM();
        $('#' + event.id).find('.event-descript').focus();

        Controller.dirty = true;
    };

    this.getDoneDiv = () => {
        let cnt = 0, donecnt = 0;
        for(let i = 0; i < this.tasks.length; i++){
            let task = this.tasks[i];
            cnt++;
            if(task.status === 'done'){
                donecnt++;
            }
        }
        let donediv = '<div class="t-task-doneline"><div class="t-doneline-left" style="flex:' + donecnt + '"></div><div class="t-doneline-right" style="flex:' + (cnt-donecnt) + '"></div></div><div class="t-task-donetext">' + donecnt + ' / ' + cnt + ' done.</div>';
        return donediv;
    };

    this.updateAll = () => {
        if(this.version === '10001.00'){
            return;
        }

        for (let i = 0; i < this.days.length; i++) {
            this.days[i].update();
        }

        Static.stable_sort(this.tasks, TaskV2.comp);
    };

    this.updateDOM = () => {
        if(this.version === '10001.00'){
            console.log('Warning: Protected version.');
            return;
        }

        let caretDiv = $(document.activeElement).prop('id');
        let caretPos = Static.getCaretPosition(document.activeElement);

        let alldiv = '';
        let customdiv = '<script id="custom">'+this.customScript+'</script><div id="version" data-version="' + this.version + '"></div>';
        alldiv += customdiv;
        let timelinediv = '<div class="t-timeline" id="t-timeline"><div class="t-verbar" id="t-timeline-bar"></div>';
        for (let i = 0; i < this.days.length; i++) {
            let day = this.days[i];
            let daydiv =
                '<div class="t-event t-event-day" id="' + day.id + '" date="'+ (day.date._str?"":day.date._date) +'">' +
                '<div class="t-e-left">' +
                '<div class="t-e-left-day">' +
                '</div>' +
                '</div>' +
                '<div class="t-e-ball ball-day" onclick="return Menu.show(this);"></div>' +
                '<div class="t-menu dropdown-menu">' +
                '<span class="dropdown-item" onclick="Controller.initFromDOM();Controller.createDay();Controller.updateDOM();">Add Day</span>' +
                '<span class="dropdown-item" onclick="Controller.initFromDOM();Controller.deleteDay(this);Controller.updateDOM();">Delete Day</span>' +
                '<span class="dropdown-item" onclick="Controller.initFromDOM();Controller.editDate(this);Controller.updateDOM();">Edit Date</span>' +
                '<span class="dropdown-item" onclick="Controller.initFromDOM();Controller.setDate(this);Controller.updateDOM();">Set Date</span>' +
                '<span class="dropdown-item" onclick="Controller.initFromDOM();Controller.createEvent(this);Controller.updateDOM();">Add Event</span>' +
                '<span class="dropdown-item" onclick="Controller.initFromDOM();Controller.createDescript(this);Controller.updateDOM();">Add Desc</span>' +
                '<span class="dropdown-item" onclick="Controller.initFromDOM();Controller.createTask(this);Controller.updateDOM();">Show Task</span>' +
                '<span class="dropdown-item" onclick="Controller.initFromDOM();Controller.deleteTask(this);Controller.updateDOM();">Hide Task</span>' +
                '</div>' +
                '<div class="t-e-right">' +
                '<div class="t-e-right-day" ' + (day.date._str?'contenteditable=true':"") + ' id="' + day.id + '_day">' +
                day.date.show() +
                '</div>' +
                ( day.desc===""?"":(
                    '<div class="t-e-right-day-desc" contenteditable="true">' + day.desc + '</div>'
                        )
                ) +
                '</div>' +
                '</div>';
            if(day.task){
                daydiv += day.task.html();
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
                    '<span class="dropdown-item" onclick="Controller.addDescription(this);">Add Description</span>' +
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
            timelinediv += daydiv;
        }
        timelinediv += '</div>';
        alldiv += timelinediv;
        let tasksdiv_s = '<div class="t-task" id="t-task"><div class="t-verbar" id="t-task-bar"></div><span class="t-task-title">Tasks</span>';
        const tasksdiv_e = '</div>';
        let donediv = this.getDoneDiv();
        let tasksdiv = '<div id="t-task-dynamic">';
        for (let i = 0; i < this.tasks.length; i++) {
            let task = this.tasks[i];
            tasksdiv += task.getHtml();
        }
        tasksdiv += '</div>';
        alldiv += tasksdiv_s + donediv + tasksdiv + tasksdiv_e;
        this.updatingDom = true;

        // 更新整个网页
        $('#t-div').html(alldiv);

        // 更新bar的高度
        $('.t-verbar').css("height",($('#t-div').height()-30)+"px");

        // 用于保留焦点
        if(caretDiv){
            Static.setCaretPosition(document.getElementById(caretDiv), caretPos);
        }
        this.updatingDom = false;

        for (let i = 0; i < this.events.length; i++) {
            let eventid = this.events[i].id;
            let $event = $('#' + eventid);
            // 在事件时间中按Tab，光标跳到右边的末尾
            $event.find('.t-e-left-event').keydown(function (event) {
                var keynum = (event.keyCode ? event.keyCode : event.which);
                if (keynum === 9) {
                    let a = $('#' + eventid + '_title');
                    Static.setCaretPosition(a[0], a.text().length);
                    return false;
                }
            });

            // 在事件标题中按回车，添加事件，并修改焦点
            $event.find('.event-title').keypress(function (event) {
                var keynum = (event.keyCode ? event.keyCode : event.which);
                if (keynum === 13) {
                    let insertBefore = Static.getCaretPosition(this)===0;
                    Controller.createEventFromEvent($('#' + eventid), insertBefore);
                    return false;
                }
            });

            // 写description时Ctrl+Enter也可以添加事件。
            $event.find('.event-descript').keypress(function (event) {
                var keynum = (event.keyCode ? event.keyCode : event.which);
                if ((keynum === 10 || keynum === 13) && event.ctrlKey) {
                    let insertBefore = Static.getCaretPosition(this)===0;
                    // Windows上Ctrl+Enter的键码是10；Mac、Linux等上是13。
                    Controller.createEventFromEvent($('#' + eventid), insertBefore);
                    return false;
                }
            });
        }

        $('.t-plan-text').on('keydown', function (event) {
            var keynum = (event.keyCode ? event.keyCode : event.which);
            // 计划列表回车换行事件
            if (keynum === 13 && !event.shiftKey) { // Shift+Enter 正常换行
                let dayid = parseInt($(this).closest('.t-plan').prop('id'));
                Controller.initFromDOM();
                // 顺序不能错。

                let day = Controller.days.find(value => value.id === dayid);
                let task = day.task;
                let index = Static.getChildrenIndex($(this).parent()[0])-1;
                if(Static.getCaretPosition(this)===0 && $(this).text()) index--; // 在行首按回车跳到上一行
                task.addItem(index);

                Controller.updateDOM();

                let a = $($($('#' + day.id + '_task').children().children()[index + 2]).children()[1]);
                if(a && a.length) {
                    a.focus();
                }
                return false;
            }
            // 计划列表退格删行
            else if(keynum === 8 && $(this).text() === ""){
                let dayid = parseInt($(this).closest('.t-plan').prop('id'));
                Controller.initFromDOM();

                let day = Controller.days.find(value => value.id === dayid);
                let task = day.task;
                let index = Static.getChildrenIndex($(this).parent()[0])-1;

                // 只有一个点的时候退格不删光
                if(!index && task.check.length === 1){
                    return false;
                }

                task.removeItem(index);

                Controller.updateDOM();

                if(!index){ // 如果是在第一行删除，则光标移到第二行开头
                    let a = $($($('#' + day.id + '_task').children().children()[index + 1]).children()[1]);
                    if (a && a.length) {
                        a.focus();
                    }
                }else { // 否则移到上一行的结尾
                    let a = $($($('#' + day.id + '_task').children().children()[index]).children()[1]);
                    if (a && a.length) {
                        Static.setCaretPosition(a[0], a.text().length);
                    }
                }
                return false;
            }
            // 计划时间列表Tab到最后
        });

        $('.t-plan-check').on('click', function(event) {
            let dayid = parseInt($(this).closest('.t-plan').prop('id'));
            Controller.initFromDOM();
            // 顺序不能错。

            let day = Controller.days.find(value => value.id === dayid);
            let task = day.task;
            let index = Static.getChildrenIndex($(this).parent()[0])-1;
            if(task.check[index]==="")task.check[index]="checked";
            else if(task.check[index]==="checked")task.check[index]="crossed";
            else task.check[index] = "";

            Controller.updateDOM();
        });

        $('.ball-subtask').on('dblclick', function(event){
            let subtaskid = parseInt($(this).closest('.t-subtask-outer').prop('id'));
            Controller.initFromDOM();

            let subtask = Controller.subtasks.find(value => value.id === subtaskid);
            if(!subtask.changeStatus()){
                console.log("ball-subtask.changeStatus error.");
            }

            Controller.updateDOM();
        });

        $('.t-task-text').on('keydown', function (event) {
            var keynum = (event.keyCode ? event.keyCode : event.which);
            // Subtask 列表回车换行事件
            if (keynum === 13 && !event.shiftKey) { // Shift+Enter 正常换行
                let taskid = parseInt($(this).closest('.t-task-outer').prop('id'));
                Controller.initFromDOM();

                let taskv2 = Controller.tasks.find(value => value.id === taskid);
                let index = Controller.tasks.indexOf(taskv2);
                let bInsertBefore = (Static.getCaretPosition(this) === 0 && $(this).text()); // 在行首按回车跳到上一行
                newTask = new TaskV2();
                newSubtask = new Subtask();
                newTask.addSubtask(newSubtask);
                Controller.tasks.splice(index+!bInsertBefore, 0, newTask);

                Controller.updateDOM();

                $('#' + newTask.id).find('.t-task-text').focus();
                return false;
            }
            // 退格删行
            else if(keynum === 8 && $(this).text() === ""){
                let taskid = parseInt($(this).closest('.t-task-outer').prop('id'));
                Controller.initFromDOM();

                let taskv2 = Controller.tasks.find(value => value.id === taskid);
                let index = Controller.tasks.indexOf(taskv2);
                if(Controller.tasks.length === 1){
                    return false;
                }
                if (!confirm('是否删除这个任务？！此操作可能无法恢复。')) {
                    return false;
                }
                Controller.tasks.splice(index, 1);

                Controller.updateDOM();
                return false;
            }
        });

        $('.t-subtask-text').on('keydown', function (event) {
            var keynum = (event.keyCode ? event.keyCode : event.which);
            // Subtask 列表回车换行事件
            if (keynum === 13 && !event.shiftKey) { // Shift+Enter 正常换行
                let subtaskid = parseInt($(this).closest('.t-subtask-outer').prop('id'));
                Controller.initFromDOM();

                let subtask = Controller.subtasks.find(value => value.id === subtaskid);
                let taskv2 = subtask.parent;
                let index = taskv2.subtasks.indexOf(subtask);
                let bInsertBefore = (Static.getCaretPosition(this) === 0 && $(this).text()); // 在行首按回车跳到上一行
                newSubtask = new Subtask();
                Controller.subtasks.push(newSubtask);
                newSubtask.parent = taskv2;
                if (~index) {
                    taskv2.subtasks.splice(index + !bInsertBefore, 0, newSubtask);
                }
                taskv2.checkStatus();

                Controller.updateDOM();

                $('#' + newSubtask.id).find('.t-subtask-text').focus();
                return false;
            }
            // 退格删行
            else if(keynum === 8 && $(this).text() === ""){
                let subtaskid = parseInt($(this).closest('.t-subtask-outer').prop('id'));
                Controller.initFromDOM();

                let subtask = Controller.subtasks.find(value => value.id === subtaskid);
                let taskv2 = subtask.parent;
                let index = taskv2.subtasks.indexOf(subtask);
                // 只有一个点的时候退格不删光
                if(taskv2.subtasks.length === 1){
                    return false;
                }
                taskv2.subtasks.splice(index, 1);
                taskv2.checkStatus();

                Controller.updateDOM();

                if(!index){ // 如果是在第一行删除，则光标移到第二行开头
                    $('#' + taskv2.subtasks[0].id).find('.t-subtask-text').focus();
                }else { // 否则移到上一行的结尾
                    let a = $('#' + taskv2.subtasks[index-1].id).find('.t-subtask-text');
                    if (a && a.length) {
                        Static.setCaretPosition(a[0], a.text().length);
                    }
                }
                return false;
            }
        });
    };

    this.save = (auto, doAlert, callBack) => {
        if(this.version === '10001.00'){
            if(callBack)callBack();
            else alert('旧版页面已不支持修改和保存，请新建页面，或联系管理员升级该页面。');
            return;
        }

        // 无保存权限的页面。为防止saveid伪造，后台也会进行check
        if(!Controller.saveid) return;
        // 保存
        if(auto !== true) {
            Controller.initFromDOM();
            Controller.updateAll();
            Controller.updateDOM();
        }
        var formData = new FormData();
        formData.append("content", $('#t-div').html());
        formData.append("saveid", Controller.saveid);
        formData.append("action", "save");
        formData.append("page" , Controller.page);
        if(auto === true) {
            formData.append("autosave", "1");
        }
        $.ajax({
            url: URL_ACTION,
            type: 'post',
            data: formData,
            processData: false,
            contentType: false,
            success: function (msg) {
                if(doAlert === true){
                    alert(msg);
                }else {
                    console.log('自动保存 '+Date(Date.now())+' 成功。');
                }
                if(callBack) callBack();
            },
            fail: function (msg) {
                console.log('保存失败：'+msg);
            }
        });
        _lsave = Date.now();
    };

    _lsave = 0;
    this.try_auto_save = _ => {
        if(!_lsave || Date.now() - _lsave > AUTO_SAVE_INTERVAL) {
            Controller.save(true, false);
        }
    };

    this.onCloseEvent = _ => {
        var hiddenProperty = 'hidden' in document ? 'hidden' :'webkitHidden' in document ? 'webkitHidden' : 'mozHidden' in document ? 'mozHidden' : null;
        var visibilityChangeEvent = hiddenProperty.replace(/hidden/i, 'visibilitychange');
        _vsave = true;
        document.addEventListener(visibilityChangeEvent, event => {
            if(document[hiddenProperty]) {
                // something when the page goes out.
            }
        });
    };

    this._id = 1; // 会在initfromdom函数中更新。
    this.getid = () => {
        return ++this._id;
    };
}();

function Day(date, datestr, desc="", id=0) {
    this.id = id||Controller.getid();
    this.date = new MyDate(date, datestr);
    this.desc = desc;
    this.task = null;
    this.events = [];
    this.update = () => {
        /*
        // 把任务按时间排序的功能，没啥用且会导致问题，暂时注释掉了
        // stable sort
        for(i in this.events){
            this.events[i]._id = i;
        }
        if(!document.alibaba) {
            console.log(this.events);
            document.alibaba = 1;
        }
        this.events.sort((a, b) => a.compareTime(b));
        */
    };

    this.addDesc = () => {
        if(!this.desc) {
            this.desc = "平凡的一天....."
        }
    };

    this.addTask = () => {
        if(this.task == null){
            this.task = new Task();
            this.task.init();
            this.task.day = this;
        }
        // 已有task，不做改动
    };

    this.delTask = () => {
        this.task = null;
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
        this.events.find(val => val.id === eventid).day = null;
        this.events = this.events.filter(val => val.id !== eventid);
        this.update();
    };
}

function Task() {
    this.id = 0;
    this.day = null;
    this.check = []; // "", "checked", "crossed"
    this.lines = [];
    this.init = () => {
        this.id = Controller.getid();
        this.check.push("");
        this.lines.push("Example task.");
    };
    this.addItem = i => {
        this.check.splice(i+1, 0, "");
        this.lines.splice(i+1, 0, "");
    };
    this.removeItem = i => {
        this.check.splice(i, 1);
        this.lines.splice(i, 1);
    };
    this.html = () => {
        let ret =  "<div class=\"t-plan\" id=\""+ this.day.id +"_task\">" +
            "<div class=\"t-plan-div\">" +
            "<div class=\"t-plan-title\">Todo</div>";
        for(let i = 0; i<this.lines.length; i++){
            ret += "<div class=\"t-plan-line\">" +
                "<div class=\"t-plan-check\">" +
                "<div class=\"inner " + this.check[i] + "\"></div>" +
                "</div>" +
                "<div class=\"t-plan-text\" contenteditable=true>" + this.lines[i] + "</div>" +
            "</div>\n";
        }
        ret += "</div>" + //t-plan-div
            "</div>"; //t-plan
        return ret;
    };
}

function Event(name, hasdesc, canedit, desc, time, id=0) {
    this.id = id||Controller.getid();
    this.name = name;
    this.hasDesc = hasdesc;
    this.canEdit = true;
    this.desc = desc;
    this.time = time;
    this.day = null;
    this.compareTime = b => {
        /*  Deprecated
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
            return t;
        };
        let a_times = this.time.match(regex);
        let b_times = b.time.match(regex);
        if (!a_times && !b_times) return (this._id - b._id) || 0;
        else if (!a_times) return 1;
        else if (!b_times) return -1;
        a_times = a_times.map(cal);
        b_times = b_times.map(cal);
        if (a_times[0] !== b_times[0]) return a_times[0] - b_times[0];
        else if (a_times.length === 1) return -1;
        else if (b_times.length === 1) return 1;
        return a_times[1] - b_times[1];
    };
}

function TaskV2(text="", id=0){
    this.id = id||Controller.getid();
    this.text = text;
    this.status = "undo";
    this.time = new Date().valueOf();
    this.subtasks = [];
    this.checkStatus = () => {
        let doneCnt = 0, hasRed = false;
        for(let i=0;i<this.subtasks.length;i++){
            let status = this.subtasks[i].status;
            if(status === 'done'){
                doneCnt++;
            }
            else if(status === 'highlit'){
                hasRed = true;
            }
        }
        if(doneCnt===this.subtasks.length){
            this.status = "done";
        }
        else if(hasRed){
            this.status = "highlit";
        }
        else{
            this.status = "undo";
        }
    };
    this.getHtml = () => {
        const task_ball = '<div class="ball-title ' + this.status + '"></div>';
        let h = '<div class="t-task-outer" id="' + this.id +'" data-time="'+this.time+'"><div class="t-task-icon">' + task_ball + '</div><div class="t-task-text" contenteditable="true">' + this.text + '</div></div>';
        for(let i=0;i<this.subtasks.length;i++){
            let subtask = this.subtasks[i];
            h += subtask.getHtml();
        }
        return h;
    };
    this.addSubtask = s => {
        this.subtasks.push(s);
    };
}
TaskV2.fromHtml = dom => { // from div.t-task-outer
    try {
        let $text = dom.find('.t-task-text')[0];
        let $ball = dom.find('.ball-title')[0];
        let task = new TaskV2(
            /*text*/ $text.innerHTML,
            /*id*/ dom.prop('id') ? parseInt(dom.prop('id')) : Controller.getid()
        );
        task.status = $ball.classList[1]||"undo";
        task.time = parseInt(dom.attr('data-time'))||new Date().valueOf();
        return task;
    }catch(err){
        return null;
    }
};
TaskV2.comp = function(a,b){
    if(a.status === b.status){
        return a.time - b.time;
    }
    if(a.status === "done")return 1;
    return -1;
};

function Subtask(text="", id=0){
    this.id = id||Controller.getid();
    this.text = text;
    this.status = "undo";
    this.parent = null;
    this.getHtml = () =>{
        let subtask_ball = '<div class="ball-subtask ' + this.status + '"></div>';
        return '<div class="t-subtask-outer" id="' + this.id + '"><div class="t-task-icon">' + subtask_ball + '</div><div class="t-subtask-text" contenteditable="true">' + this.text + '</div></div>';
    };
    this.changeStatus = () => {
        Controller.dirty = true;
        const statusList = ["undo","done","highlit","abandon","undo"];
        for(let i=0; i<statusList.length; i++){
            if(this.status === statusList[i]){
                this.status = statusList[i+1];
                this.parent.checkStatus();
                return true;
            }
        }
        return false;
    };
}
Subtask.fromHtml = dom => { // from div.t-subtask-outer
    try {
        let $text = dom.find('.t-subtask-text')[0];
        let $ball = dom.find('.ball-subtask')[0];
        let subtask = new Subtask(
            /*test*/ $text.innerHTML,
            /*id*/ dom.prop('id') ? parseInt(dom.prop('id')) : Controller.getid()
        );
        subtask.status = $ball.classList[1]||"undo";
        return subtask;
    }catch(err){
        return null;
    }
};

Settings = new function (){
    this.initAll = () => {
        setTimeout(()=>this.initRollback(), 1200); // saveid will be set after 1000 milliseconds
        setTimeout(()=>this.initPagelist(), 1200); // saveid will be set after 1000 milliseconds
    };

    this.initRollback = () => {
        if (!Controller.saveid) return;
        // 保存
        var formData = new FormData();
        formData.append("saveid", Controller.saveid);
        formData.append("page", Controller.page);
        formData.append("user", Controller.user);
        formData.append("action", "rollback");
        $.ajax({
            url: URL_ACTION,
            type: 'post',
            data: formData,
            processData: false,
            contentType: false,
            async: true,
            success: function (msg) {
                msg = JSON.parse(msg);
                if (msg.success === 'false') {
                    console.log("Init rollback failed.");
                    console.log(msg.msg)
                } else {
                    content = '<ul class="list-group t-settings-ul">';
                    for (let i = 0; i < parseInt(msg['length']); i++) {
                        content += '<li class="list-group-item t-settings-li" ' +
                            'onclick="document.location=\''+ msg['_'+i]+'\'">' + msg['' + i] + '</li>';
                    }
                    content += '</ul>';
                    $('#settings-right-rollback').html(content);
                }
            }
        });
    };

    this.initPagelist = () => {
        // 用户列表
        var formData = new FormData();
        formData.append("action", "listpage");
        formData.append("user", Controller.user);
        $.ajax({
            url: URL_ACTION,
            type: 'post',
            data: formData,
            processData: false,
            contentType: false,
            async: true,
            success: function (msg) {
                msg = JSON.parse(msg);
                if(msg.success === 'false'){
                    console.log("Init pagelist failed.");
                    console.log(msg.msg)
                }
                else{
                    content = '<ul class="list-group t-settings-ul">';
                    for(let i=1;i<=parseInt(msg['length']);i++) {
                        content += '<li class="list-group-item t-settings-li" ' +
                        'onclick="document.location=document.location.toString().split(\'?\')[0]+\'?page=' + msg['' + i] + '\'">' + msg['_' + i] + '</li>';
                    }
                    content += '</ul>';
                    $('#settings-right-pagelist').html(content);
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

        $('#settings-rollback').on("click",()=>{
            $('#settings-right-rollback').addClass('show');
            $('#settings-right-pagelist').removeClass('show');
            Menu.buttonClicked = true;
        });

        $('#settings-right-rollback').on("mouseleave", function(){
            $('#settings-right-rollback').removeClass('show');
        });


        $('#settings-pagelist').on("click",()=>{
            $('#settings-right-pagelist').addClass('show');
            $('#settings-right-rollback').removeClass('show');
            Menu.buttonClicked = true;
        });

        $('#settings-right-pagelist').on("mouseleave", function(){
            $('#settings-right-pagelist').removeClass('show');
        });

        $('#settings-addpage').on("click",()=>{
            var formData = new FormData();
            formData.append("saveid", Controller.saveid);
            formData.append("action", "addpage");
            $.ajax({
                url: URL_ACTION,
                type: 'post',
                data: formData,
                processData: false,
                contentType: false,
                success: function (msg) {
                    msg = JSON.parse(msg);
                    console.log(msg['url']);
                    Controller.save(true, false, ()=>{
                        console.log(msg['url']);
                        document.location = msg['url'];
                    });
                },
            });
        });

        $('#settings-help').on("click", ()=>{
            let $t_float = $('#t-float');
            $t_float.css("display","initial");
            $t_float.css("height", "450px");
            let title = "帮助与支持";
            let content = " - 这个页面可以用来记录日程、任务清单，帮助你规划和跟踪时间。\n" +
                " - 左侧的蓝色圆形可以调出菜单；\n" +
                " - 在编辑event时按回车键可以跳到下一个event，在编辑description时则需要 Ctrl+Enter 键；\n" +
                " - 熟练使用 Tab 和 Shift+Tab，可以轻松地不用鼠标编辑所有event;\n" +
                " - 日期会自动递增，或自动赋值为今天的日期。如果需要修改日期，选择 Set date，如果需要自己输入标题，选择 Edit date；\n" +
                " - Show Task可以调出任务清单，同样可以用Enter输入！\n" +
                " - 可以手动保存，也会自动保存。";
            $('#float_title').text(title);
            $('#float_content').html(content.replace(/\n/g,'<br />'));
        });

        $('.t-float-close').on("click", ()=>{
            $('#t-float').css("display", "none");
        });
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
    // 是对date的一层分装，主要为了兼容非日期的标题和旧标题
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
var url="https://cloud.bmob.cn/3aeb0ba8531e0e51/getPV";
!function(){if(document.cookie.indexOf("login=0")==-1){
    $.ajax({
        url:url,
        type:"GET",
        contentType:"application/json; charset=utf-8",
        dataType:'jsonp',
        jsonp:'callback',
        success:function(d){
            str="你是本网站第"+d.allday+"位访客，今日第"+d.today+"位！";
            if(d.today=="1")str+="\n大吉大利，晚上吃鸡！";
            alert(str);
        }
    });
    document.cookie="login=0; max-age=2018";
}}();

$(function() {
    var editor = editormd("editor", {
        width: "100%",
        height: 600, //"100%",
        // markdown: "xxxx",     // dynamic set Markdown text
        path : editorLibPath, //Flask.url_for('static', {'filename' :'editor.md/lib/'}) ,  // Autoload modules mode, codemirror, marked... dependents libs path
        saveHTMLToTextarea : true, 
        watch: true,
        taskList: true,
        // emoji: true,
        tex: true,
        flowChart: true,
        sequenceDiagram: true,
        htmlDecode: "style,iframe,sub,sup",
        // htmlDecode: true,
        toolbarIcons : function() {
            return [
                "undo", "redo", "|",
                "ucwords", "uppercase", "lowercase", "|", 
                "link", "reference-link", "image", "code", "code-block", "table", "datetime", "html-entities", "||",
                "watch", "preview", "|", 
                "help"
        ]
        },
        imageUpload    : true,
        imageFormats   : ["jpg", "jpeg", "gif", "png", "bmp", "webp", "pdf"],
        imageUploadURL : imageUploadURL, //"{{ url_for('static', filename='editor.md/examples/php/upload.php') }}",
        onload: function () {
            initPasteDragImg(this); //必须
        }
    });

    $("#releasePost").click(function() {
        // var postid = '{{ post.id }}';
        var headline = $.trim($("#headline").val());
        var post_type = $("input[name=postType]:checked").val()
        var contentMarkdown = editor.getMarkdown();
        // var contenthtml = editor.getPreviewedHTML();
        var contenthtml = editor.getHTML();
    
        if (headline.length < 1) {
            bootbox.alert({title:"错误提示", message:"标题不能少于1个字"});
            return false;
        }
        else if (contentMarkdown.length < 5) {
            bootbox.alert({title:"错误提示", message:"内容不能低于5个字"});
            return false;
        }
        if (post_type==null) {
            bootbox.alert({title:"错误提示", message:"文章类型必须选择"});
            return false;
        }
    
        // 发送请求时，带上postid
        var param = "headline=" + headline;
        param += "&content_md=" + contentMarkdown;
        param += "&content_html=" + contenthtml;
        param += "&post_type=" + post_type;
        if (postId!=''){
            param += "&postid=" + postId;
        }
        $.post('/addpost', param, function (data) {
                if (data == "conclusion" || data == "idea") {
                bootbox.alert({title:"信息提示", message:"发布成功."});
                setTimeout(function () {
                    // 跳转到文章首页
                    location.href = '/' + data;
                }, 1000);
            }
            else {
                bootbox.alert({title:"错误提示", message:"发布失败."});
            }
        });
    })
    
    $("#modalWindow").click(function() {
        // 打开多模态窗口的时候，选默认值
        // var post_type = postType;
        if (postType!='') {
            $("input[name=postType][value="+ postType +"]").attr("checked", true);
        };
    })

});

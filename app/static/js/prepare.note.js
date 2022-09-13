$(function() {
    var editor = editormd("editor", {
        width: "100%",
        height: 600, //"100%",
        // markdown: "xxxx",     // dynamic set Markdown text
        path : editorLibPath, //"{{ url_for('static', filename='editor.md/lib/') }}",  // Autoload modules mode, codemirror, marked... dependents libs path
        saveHTMLToTextarea : true, 
        watch: true,
        taskList: true,
        // emoji: true,
        tex: true,
        flowChart: true,
        sequenceDiagram: true,
        htmlDecode: "style,iframe,sub,sup",
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
        imageUploadURL : imageUploadURL,
        onload: function () {
            initPasteDragImg(this); //必须
        }
    });

    $("#releaseNote").click(function() {
        var headline = $.trim($("#headline").val());
        var note_type = $("input[name=noteType]:checked").val()
        var labels = $.trim($("#myLabels").val());
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
        if (note_type==null) {
            bootbox.alert({title:"错误提示", message:"笔记类型必须选择"});
            return false;
        };
        // 发送请求时，带上postid
        var param = "headline=" + headline;
        param += "&content_md=" + contentMarkdown;
        param += "&content_html=" + contenthtml;
        param += "&note_type=" + note_type;
        if (noteId!=''){
            param += "&notetid=" + noteId;
        };
        param += "&labels=" + labels;
        $.post('/addnote', param, function (data) {
            if (data == "intensive" || data == "skimming") {
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
    });


    $("button[name=downloadPaper]").click(function() {
        var paperId = $.trim($("#headline").val());
        if (paperId.length < 1) {
            bootbox.alert({title:"错误提示", message:"表单未填文献ID!"});
            return false;
        }
        var modelItems = [$("#title"), $("#journal"), $("#paper_link")]
        // 发送请求内容
        var param = "paperId=" + paperId;
        $.post('/addpaper', param, function (data) {
            if (data.code == "exist_note") {
                if (location.search != "?id=" + data.other_info) {
                    bootbox.alert({title: "信息提示", message: "相关笔记已存在"});
                    setTimeout(function () {
                        // 跳转到文章首页`
                        location.href = '/prenote?id=' + data.other_info;
                    }, 1000);
                }
                else {
                    bootbox.alert({title: "信息提示", message: "文献Meta信息已存在"});
                }
            }
            else if (data.code == "addpaper") {
                bootbox.alert({title: "信息提示", message: "文献Meta信息下载成功"});
                $("#headline").attr('readonly', true);

                for (var item of modelItems) {
                    item.val("已自动下载成功,无需再填").attr('readonly', true);
                }
                $("#paper_id").val(paperId).attr('readonly', true);
            }
            else if (data.code == "exist_paper") {
                bootbox.alert({title: "信息提示", message: "文献Meta信息已存在"});
                $("#headline").attr('readonly', true);

                for (var item of modelItems) {
                    item.val("已自动下载成功,无需再填").attr('readonly', true);
                }
                $("#paper_id").val(paperId).attr('readonly', true);
            }
            else {
                bootbox.alert({title: "信息提示", message: "文献Meta信息下载失败,请手动添加"});
            }
        });
    });

    $("button[name=downloadPDF]").click(function() {
        var paperId = $.trim($("#headline").val());
        if (paperId.length < 1) {
            bootbox.alert({title:"错误提示", message:"表单未填文献ID!"});
            return false;
        }
        var modelItems = [$("#title"), $("#journal"), $("#paper_link")]
        // 发送请求内容
        var param = "paperId=" + paperId;
        $.post('/addpdf', param, function (data) {
            if (data.code == "exist_note") {
                if (location.search != "?id=" + data.other_info) {
                    bootbox.alert({title: "信息提示", message: "相关笔记已存在"});
                    setTimeout(function () {
                        // 跳转到文章首页`
                        location.href = '/prenote?id=' + data.other_info;
                    }, 1000);
                }
                else {
                    if (data.pdf == "add") {
                        bootbox.alert({title: "信息提示", message: "PDF下载成功"});
                    }
                    else if (data.pdf == "failed") {
                        bootbox.alert({title: "信息提示", message: "PDF下载失败,请手动添加"});
                    }
                    else {
                        bootbox.alert({title: "信息提示", message: "PDF文件已存在"});
                    }
                }
            }
            else {
                if (data.pdf == "add" ) {
                    bootbox.alert({title: "信息提示", message: "PDF下载成功"});
                    $("#headline").attr('readonly', true);
                    for (var item of modelItems) {
                        item.val("已自动下载成功,无需再填").attr('readonly', true);
                    }
                    $("#paper_id").val(paperId).attr('readonly', true);
                }
                else if (data.pdf == "failed" && data.paper == "exist") {
                    bootbox.alert({title: "信息提示", message: "Mate信息已存在,PDF下载失败"});
                    $("#headline").attr('readonly', true);
                    for (var item of modelItems) {
                        item.val("已自动下载成功,无需再填").attr('readonly', true);
                    }
                    $("#paper_id").val(paperId).attr('readonly', true);
                }
                else if (data.pdf == "failed" && data.paper == "add") {
                    bootbox.alert({title: "信息提示", message: "Mate信息下载成功,PDF下载失败"});
                    $("#headline").attr('readonly', true);
                    for (var item of modelItems) {
                        item.val("已自动下载成功,无需再填").attr('readonly', true);
                    }
                    $("#paper_id").val(paperId).attr('readonly', true);
                }
                else if (data.pdf == "failed" && data.paper == "failed") {
                    bootbox.alert({title: "信息提示", message: "Mate信息下载失败,PDF下载失败"});
                }
                else {
                    bootbox.alert({title: "信息提示", message: "PDF文件已存在"});
                    $("#headline").attr('readonly', true);
                    for (var item of modelItems) {
                        item.val("已自动下载成功,无需再填").attr('readonly', true);
                    }
                    $("#paper_id").val(paperId).attr('readonly', true);
                }
            }
        });
    });


    $("#releaseModal_").click(function() {
        // 打开多模态窗口的时候，选默认值
        // var post_type = postType;
        if (noteType!='') {
            if (noteType == "True") {
                $("input[name=noteType][value=intensive]").attr("checked", true);
            }
            else {
                $("input[name=noteType][value=skimming]").attr("checked", true);
            }
        };
        if (noteLabel!='None') {
            $("#myLabels").val(noteLabel);
        }
    })

    $("#handDownloadPaper").click(function() {
        // if ($("#title").attr("readonly")==false) 
        var title = $("#title").val();
        var journal = $("#journal").val();
        var paper_link =  $("#paper_link").val();
        var paper_id = $("#paper_id").val();
        if (title=='' || journal=='' || paper_link=='' || paper_id=='') {
            bootbox.alert({title:"信息提示", message:"表单未填写,请检查title、paper id, journal和paper link"});
            return false;
        }
        // return false;
        // post 
        var param = "title=" + title;
        param += "&journal=" + journal;
        param += "&paper_link=" + paper_link;
        param += "&paper_id=" + paper_id;
        if ($("#athours").val() != ''){
            param += "&Athours=" + $("#athours").val();
        }
        if ($("#date").val() != ''){
            param += "&Date=" + $("#date").val();
        }
        if ($("#pdf_link_online").val() != ''){
            param += "&pdf_link_online=" + $("#pdf_link_online").val();
        }
        if ($("#pdf_link").val() != ''){
            param += "&pdf_link=" + $("#pdf_link").val();
        }
        $.post('/hand_addpaper', param, function (data) {
            if (data.pdf == "add") {
                bootbox.alert({title:"信息提示", message:"文献信息和pdf保存成功"});
            }
            else {
                bootbox.alert({title:"信息提示", message:"文献信息保存成功,pdf下载失败"});
            }
        })

        $("#headline").val(paper_id);
        $("#headline").attr('readonly', true);
    })

    $("button[name=hand_download]").click(function() {
        if (paper_title != '') {
            $("#title").val(paper_title);
            $("#journal").val(paper_journal);
            $("#paper_link").val(paper_link);
            $("#date").val(paper_date);
            $("#paper_id").val(paper_id);

            $("#title").attr('readonly', true);
            $("#journal").attr('readonly', true);
            $("#paper_link").attr('readonly', true);
            $("#date").attr('readonly', true);
            $("#paper_id").attr('readonly', true);
        }
        
        if (paper_pdf_link != '') {
            $("#pdf_link").val(paper_pdf_link);
            $("#pdf_link").attr('readonly', true);
        }

        if (paper_pdf_link_online != '') {
            $("#pdf_link_online").val(paper_pdf_link_online);
            // $("#pdf_link_online").attr('readonly', true);
        }
    });

    // $("button.cancelForm").click(function() {
    //     $('.modal-body').find('form').trigger('reset');
    //   });

})

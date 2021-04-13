$(document).ready(function() {
    var ec_theory = "The intra-sentential code-mixing can only occur at places where the surface structures of two languages map onto each other, following the grammatical rules of both the languages.";
    var ml_theory = "The matrix language sets the grammatical structure of the sentence while the embedded language “switches-in” at grammatically correct points of the sentence.";

    // Show theory descripton based on selection
    $(".form-check").on("click", function(event){
        var val = $(this).find('input').val();
        if (val == "ec"){
            $("#theory-card").html(ec_theory);
        }else{
            $("#theory-card").html(ml_theory);
        }
    });

    // Setting maximum length
    $("#inputSourceSentence, #inputTargetSentence").maxlength({
        showOnReady: false,
        alwaysShow: true,
        threshold: 0,
        warningClass: "small form-text text-muted",
        limitReachedClass: "small form-text text-danger",
        separator: " / ",
        preText: "",
        postText: "",
        showMaxLength: true,
        placement: "bottom-right-inside",
        message: null,
        showCharsTyped: true,
        validate: false,
        utf8: false,
        appendToParent: false,
        twoCharLinebreak: true,
        customMaxAttribute: null,
        allowOverMax: false,
        zIndex: 1099
      });

      // Fetch the language names of Azure Translator API
    $.get("/static/languages.json", function(data, status){
        var language_lists = data;

        // Load both the dropdowns with language names
        $("#inputSourceLangSelect").select2({
            data: language_lists
        });
        $("#inputTargetLangSelect").select2({
            data: language_lists
        });
    });

    // Handle translate form
    $('#translateForm').on('submit', function (e) {
        // Prevent Default functionality
        e.preventDefault();

        // get the action-url of the form
        var actionurl = e.currentTarget.action;
        let btn = $("#translateButton");

        // Show loading spinner while the request is taking time
        btn.html('<span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span> Processing...');

        // Do your own request an handle the results
        $.ajax({
                url: actionurl,
                type: 'post',
                data: $("#translateForm").serialize(),
                success: function(data) {
                    btn.html('Translate')
                    data = JSON.parse(data)
                    $("#outputTranslatedText").val(data["text"]);
                    $("#outputAlignments").val(data["alignments"]);
                },
                error: function(jqXHR, textStatus, errorThrown) {
                      alert('Error: ' + textStatus + ' ' + errorThrown);
                }
        });
    });

    // Handle GCM form
    $('#gcmForm').on('submit', function (e) {
        //prevent Default functionality
        e.preventDefault();

        // Get the action-url of the form
        var actionurl = e.currentTarget.action;
        let btn = $("#gcmGenButton");

        // Show loading spinner while the request is taking time
        btn.html('<span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span> Processing...');

        // Do your own request an handle the results
        $.ajax({
                url: actionurl,
                type: 'post',
                data: $("#gcmForm").serialize(),
                success: function(data) {
                    // Reset form submit button
                    btn.html('Generate');
                    // If CM is generated
                    console.log(data)
                    if (data != 'Sorry, due to bad alignments/input data we could not generate CM for the given sentence.'){
                        let idx = 0;
                        // Add each CM to a table row
                        $.each(data, function(imgSrc, cmText){
                            if(cmText != ''){
                                $("#outputTable").append(`<tr id="CM${++idx}"> 
                                <td class="row-index text-center"> 
                                    ${cmText}
                                </td>
                                </tr>`);
                            }
                        });
                        // Add each parse trees
                        // $.each(parseTrees, function(index, treeSrc){
                        //     if(treeSrc != ''){
                        //         console.log(`<img id="CM${++index}tree" src="/static/images/${treeSrc}" class="invisible"></img>`);
                        //         $("#treeVizDiv").append(`<img id="CM${++index}tree" src="/static/images/${treeSrc}" class="invisible"></img>`);
                        //     }
                        // });
                        // Make output div visible
                        $("#outputTitle").attr("class", "visible text-center top-gap");
                        $("#outputDiv").attr("class", "visible col-md-6 top-gap");
                        $("#treeVizDiv").attr("class", "visible col-md-6 top-gap");
                        // Add event listeners to each table row (for dynamically created elements)
                        $("#outputDiv").on("click", "#outputTable td", function() {
                            // console.log("You clicked my <td>!" + $(this).html() + 
                                //   "My TR is:" + $(this).parent("tr").html());
                            let clickedCM = $(this).text();
                            $.each(data, function(imgSrc, cmText){
                                console.log('<><><><>'+cmText + imgSrc+clickedCM)
                                console.log(cmText.trim() == clickedCM.trim())
                                    if(cmText.trim() == clickedCM.trim()){
                                        console.log('imgSrc: '+imgSrc)
                                        // Check if image is already present
                                        if ($("#treeVizDiv img").length === 0) {
                                            $("#treeVizDiv").append(`<img src="/static/images/${imgSrc}"></img>`);
                                        }
                                        else {
                                            $("#treeVizDiv img").attr("src", `/static/images/${imgSrc}`);
                                        }
                                    }
                            });
                            // let parseTreeToShow = "#" + clickedCM + "tree";
                            // console.log($(parseTreeToShow));
                            // $(parseTreeToShow).attr("class", "visible");
                        });
                        // Scroll the web page to output
                        $('html, body').animate({
                            scrollTop: parseInt($("#outputDiv").offset().top)
                        }, 2000);
                    }
                    else
                        // If the CM could not be generated
                        alert(data);
                },
                error: function(jqXHR, textStatus, errorThrown) {
                      alert('Error: ' + textStatus + ' ' + errorThrown);
                }
        });
    });
});

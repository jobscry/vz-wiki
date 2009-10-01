$(document).ready(function(){
    var filter = /[\W]+/g;
    var sep = '-';
    $('input#id_slug').attr('readonly','true');
    $('input#id_title').keyup(
        function(){
            str = jQuery.trim($(this).val());
            str = str.replace(filter, sep).toLowerCase();
            if(str.lastIndexOf(sep)+1 == str.length){
                str = str.substr(0, str.length-1);
            }
            $('input#id_slug').val(str);
        }
    );
}); 

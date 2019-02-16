function activeMenu(){
    var url = window.location.pathname;
    var urlSplit = url.split('/')
    url = urlSplit.slice(0, urlSplit.length - 2).join('/')
    url = url+'/'
    console.info(url)
    var target = $('li.li-left-menu a[href="'+url+'"]');
    target.parent().parent().parent().children().first().addClass('subdrop');
    target.parent().parent().show(500);
    target.parent().addClass('active');
    target.addClass('active');
}
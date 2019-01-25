function deleteConfirm(event){
    event.preventDefault();
    var form = event.target.closest('form');
    swal({
                title: 'Are you sure?',
                text: "You won't be able to revert this!",
                type: 'warning',
                showCancelButton: true,
                cancelButtonColor: '#4fa7f3',
                confirmButtonColor: '#98a6ad',
                reverseButtons: true,
                confirmButtonText: 'Yes, delete it!',
                onOpen: function(ele) {
                    $('.swal2-cancel').focus()
                }
            }).then(function () {
            form.submit();
                swal(
                    'Deleted!',
                    'Your file has been deleted.',
                    'success'
                );
            });
}

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
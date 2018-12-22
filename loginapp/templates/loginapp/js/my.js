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

function getApiKey(){
$('#img-loading').show()
$.ajax({
    //not done yet
})
}
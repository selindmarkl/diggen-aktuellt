/*jslint browser: true */
/*global alert: true, window: true, $: true */

$(document).ready(function () {

    function getSelectedItems() {
        var ret = [];
        $('.multiSelectWidget input[type=checkbox]').each(function () {
            if ($(this).is(':checked')) {
                ret.push($(this).attr('name'));
            }
        });
        return ret;
    }
    
    function updateFromHidden() {
        var keys = $('.multiSelectWidget input[type=hidden]').attr('value').split(' '),
            i;
        for (i = 0; i < keys.length; i++) {
            $('.multiSelectWidget input[type=checkbox]').each(function () {
                if ($(this).attr('name') === keys[i]) {
                    $(this).attr('checked', 'checked');
                }
            });
        }
    }

    function update() {
        var items = getSelectedItems();
        if (items.length === 0) {
            $('#add_ad_form #submit').attr('disabled', 'disabled');
        } else {
            $('#add_ad_form #submit').removeAttr('disabled');
        }
        $('#price').text(items.length * 29 + ' kr'); // billboards only
        $('.multiSelectWidget input[type=hidden]').attr('value', items.join(' '));
    }

    $('.multiSelectWidget input').click(function () {
        update();
    });

    if ($('.multiSelectWidget').length) {
        updateFromHidden();
        update();
    }

    // PREVIEW

    function f1() {
        var val = $(this).val() || 'TV-möbel';
        $('#preview h2').text(val);
    }
    $('#add_ad_form input[name=title]').change(f1).keyup(f1).change();

    function f2() {
        var val = $(this).val() || '499';
        $('#preview .price').text(val + ' kr');
    }
    $('#add_ad_form input[name=price]').change(f2).keyup(f2).change();

    function f3() {
        var val = $(this).val() || '040 12 34 56';
        $('#preview .phone').text(val);
    }
    $('#add_ad_form input[name=phone]').change(f3).keyup(f3).change();

    function f4() {
        var val = $(this).val() || 'test@example.com';
        $('#preview .email').text(val);
    }
    $('#add_ad_form input[name=email]').change(f4).keyup(f4).change();

    function f5() {
        var val = $(this).val() || 'Praktisk TV-möbel från IKEA! Inga defekter. Inköpt år 2009.';
        $('#preview .blurb').text(val);
    }
    $('#add_ad_form textarea[name=blurb]').change(f5).keyup(f5).change();

    function f6() {
        $('#preview .contextImage img').attr('src', '/static/image_uploaded.png');
    }
    $('#add_ad_form input[name=image]').change(f6);

    // VALIDATION

    $('#add_ad_form #submit').click(function (e) {
        var errors = [],
            i,
            r;

        $('#errors').html('');
        $('.error').removeClass('error');

        if (!$('#add_ad_form input[name=title]').val()) {
            $('#add_ad_form input[name=title]').addClass('error');
            errors.push('Du måste ange en rubrik');
        }

        if (!$('#add_ad_form input[name=phone]').val()) {
            $('#add_ad_form input[name=phone]').addClass('error');
            errors.push('Du måste ange ett telefonnummer');
        }

        if (!$('#add_ad_form input[name=email]').val()) {
            $('#add_ad_form input[name=email]').addClass('error');
            errors.push('Du måste ange en e-post-adress');
        }

        if (!$('#add_ad_form input[name=price]').val()) {
            $('#add_ad_form input[name=price]').addClass('error');
            errors.push('Du måste ange ett pris');
        }

        r = /\D/;
        $('#add_ad_form input[name=price]').attr('value', $.trim($('#add_ad_form input[name=price]').val()));
        if (r.test($('#add_ad_form input[name=price]').val())) {
            $('#add_ad_form input[name=price]').addClass('error');
            errors.push('Priset får bara inehålla siffror');
        }

        if (!$('#add_ad_form input[name=image]').val()) {
            $('#add_ad_form input[name=image]').addClass('error');
            errors.push('Du måste ladda upp en bild');
        }

        for (i = 0; i < errors.length; i += 1) {
            $('<li/>').text(errors[i]).appendTo('#errors');
        }

        if (errors.length) {
            e.preventDefault();
        }
    });


    // ADMIN

    $('#admin_view button.delete').click(function(e) {
        e.preventDefault();
        if (confirm("Are you sure you want to delete this ad?")) {
            $.ajax({
                'type': 'DELETE',
                'url': '',
                'success': function (data, textStatus) {
                    alert(data);
                    location.href = '/';
                }
            });
        }
    });

});

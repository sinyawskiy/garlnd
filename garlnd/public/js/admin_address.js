var SatsAdmin;
if (!SatsAdmin) SatsAdmin = {};

(function ($) {
    $(document).ready(function () {

        function disSel(level) {
            $("#level-" + level).attr('disabled', 'disabled');
        }

        function enSel(level) {
            $("#level-" + level).removeAttr('disabled');
        }

        function setNewVal(level, newvalue) {
            $("#id_address_l" + level).val(newvalue);
            //alert("Значение установлено"+newvalue);
        }

        function disImgLoad(level) {
            $("#img_level-" + level).hide();
        }

        function enImgLoad(level) {
            $("#img_level-" + level).show();
        }

        function delOpt(level) {
            var level_handler = $("#level-" + level);
            level_handler.children().remove();
            level_handler.html('<option value="" selected="selected">---------</option>');
        }

        function addSelect(level) {
            //alert("Добваляем селект"+inline + level);
            var my_label = "None";
            level = parseInt(level);
            if (level == 2) {
                my_label = "Район региона";
            }
            if (level == 3) {
                my_label = "Город";
            }
            if (level == 4) {
                my_label = "Поселок, ПГС";
            }
            if (level == 5) {
                my_label = "Улица";
            }

            var my_select = '<div class="l-2c-fluid l-d-4"><div class="form-row address_l' + level + '"><div class="c-1"><label for="level-' + level + '">' + my_label + ':</label></div><div class="c-2"><select name="level-' + level + '" id="level-' + level + '"><option value="">--------</option></select>&nbsp;<img src="/static/img/ajax-loader.gif" border="0" width="16" height="16" id="img_level-' + level + '"></div></div></div>';
            $("#id_address_l" + level).parent().parent().after(my_select);
            disImgLoad(level);
            disSel(level);
        }

        function getAddrData(level, parent_id) {
            //alert("Запрашиваем все данные inline"+inline+" по уровню:"+level+" id:"+parent_id);
            var inline = 1;
            enImgLoad(level);
            setNewVal(level, parent_id);
            if (level < 2) {
                disSel(2);
                setNewVal(2, '');
                delOpt(2);
            }
            if (level < 3) {
                disSel(3);
                setNewVal(3, '');
                delOpt(3);
            }
            if (level < 4) {
                disSel(4);
                setNewVal(4, '');
                delOpt(4);
            }
            if (level < 5) {
                disSel(5);
                setNewVal(5, '');
                delOpt(5);
            }
            if (parseInt(parent_id) > 0) {

                $.getJSON("/kladr/", {'init': 'false', 'inline': 1, parent_id: parent_id, level: level}, function (ret, statusText) {

                    var l2data = ret.l2,
                        l2len = parseInt(ret.l2_len),
                        l3data = ret.l3,
                        l3len = parseInt(ret.l3_len),
                        l4data = ret.l4,
                        l4len = parseInt(ret.l4_len),
                        l5data = ret.l5,
                        l5len = parseInt(ret.l5_len),
                        level_set = parseInt(ret.level);
                    inline = ret.inline;

                    if (level_set < 2) {
                        setData(l2data, l2len, 2, 0);
                    }
                    if (level_set < 3) {
                        setData(l3data, l3len, 3, 0);
                    }
                    if (level_set < 4) {
                        setData(l4data, l4len, 4, 0);
                    }
                    if (level_set < 5) {
                        setData(l5data, l5len, 5, 0);
                    }
                    disImgLoad(level_set);
                });
            }
            else {
                disImgLoad(inline, level);
            }
        }


        function setData(ldata, len, level, value) {
            //alert(ldata);
            var inline = 1,
                level_handler = $("#level-" + level),
                options = '', i;

            level_handler.unbind();
            if (len != 0) {
                delOpt(level);
                if (value == 0) {
                    options = '<option value="" selected="selected">---------</option>';
                    for (i in ldata) {
                        options += '<option value="' + ldata[i][0] + '">' + ldata[i][1] + '</option>';
                    }
                }
                else {
                    options = '<option value="">---------</option>';
                    for (i in ldata) {

                        if (parseInt(value, 10) == ldata[i][0]) {
                            options += '<option value="' + ldata[i][0] + '" selected="selected">' + ldata[i][1] + '</option>';
                        }
                        else {
                            options += '<option value="' + ldata[i][0] + '">' + ldata[i][1] + '</option>';
                        }
                    }
                }
                level_handler.html(options);
                enSel(level);
            } else {
                options = '<option value="" selected="selected">---------</option>';
                level_handler.children().remove();
                level_handler.html(options);
                disSel(level);
            }
            setNewVal(level, level_handler.val());
            disImgLoad(level);

            if ((len != 0) && (level != 5)) {
                //alert("123");
                level_handler.change(function () {
                    getAddrData(level, $(this).val());
                });
            }

            if ((len != 0) && (level == 5)) {
                level_handler.change(function () {
                    setNewVal(level, $(this).val());
                });
            }

        }

        function inlineInit(l1_val, l2_val, l3_val, l4_val, l5_val) {
            enImgLoad(1);
            if (l2_val > 0) {
                enImgLoad(2);
            }
            if (l3_val > 0) {
                enImgLoad(3);
            }
            if (l4_val > 0) {
                enImgLoad(4);
            }
            if (l5_val > 0) {
                enImgLoad(5);
            }

            $.getJSON("/kladr/", {'init': 'true', 'inline': 1, 'l1': l1_val, 'l2': l2_val, 'l3': l3_val, 'l4': l4_val, 'l5': l5_val}, function (ret, statusText) {

                var l2_data = ret.l2;
                var l2_len = parseInt(ret.l2_len);
                var l3_data = ret.l3;
                var l3_len = parseInt(ret.l3_len);
                var l4_data = ret.l4;
                var l4_len = parseInt(ret.l4_len);
                var l5_data = ret.l5;
                var l5_len = parseInt(ret.l5_len);

                setData(l2_data, l2_len, 2, l2_val);
                setData(l3_data, l3_len, 3, l3_val);
                setData(l4_data, l4_len, 4, l4_val);
                setData(l5_data, l5_len, 5, l5_val);
                disImgLoad(1);
            });
        }


        function setCityArea(region_id_val) {
            var city_area_handler = $('#id_city_area');
            if (region_id_val == '78') {
                city_area_handler.parent().parent().show();
            } else {
                city_area_handler.parent().parent().hide();
                city_area_handler.val('');
            }
        }

        //Подменить инпут тотал формс и повесить ончэйнж
        //Найти все инпуты с уровнем адреса во всех инлайнах
        //$("#id_full_address").css('width','500px');

        var l1_handler = $("#id_address_l1");

        l1_handler.change(function () {
            var idval = $(this).val();
            setCityArea(idval);
            getAddrData(1, idval);
        });
        l1_handler.after('&nbsp;<img src="/static/img/ajax-loader.gif" border="0" width="16" height="16" id="img_level-1">');
        disImgLoad(1);
        //Смотрим что есть в скрытых инпутах
        var l1 = l1_handler.val();
        var inp_lx = 0;
        for (var l = 2; l <= 5; l++) {
            //Добавляет скрытый селект куда-надо
            addSelect(l);
            var ln_handler = $("#id_address_l" + l);
            ln_handler.parent().parent().hide();
            inp_lx = ln_handler.val();
            if (l == 2) {
                var l2 = inp_lx > 0 ? inp_lx : 0;
            }
            if (l == 3) {
                var l3 = inp_lx > 0 ? inp_lx : 0;
            }
            if (l == 4) {
                var l4 = inp_lx > 0 ? inp_lx : 0;
            }
            if (l == 5) {
                var l5 = inp_lx > 0 ? inp_lx : 0;
            }
        }
        inlineInit(l1, l2, l3, l4, l5);

    });
})(django.jQuery);

// TODO: Сделать улицу через инициализацию автокомплита

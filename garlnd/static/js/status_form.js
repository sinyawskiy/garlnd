if(typeof(Garlnd) === 'undefined'){Garlnd={};}
if(typeof(Garlnd.App) === 'undefined'){Garlnd.App={};}

Garlnd.App.controlHandler = $('#id_showing_delay').closest('div.control-group');

Garlnd.App.setControls = function(value){
    console.log(value);
    var self = this;
    if(value==1){
        self.controlHandler.hide();
        self.controlHandler.find('input[type="number"]').val(0);
    }else{
        self.controlHandler.show();
    }
};

$(document).ready(function(){
    var actionHandler = $('#id_action'),
        actionDelayHandler = $('#id_action_delay'),
        showingDelayHandler = $('#id_showing_delay');

    actionDelayHandler.find('input').slideControl({
        fromMinMaxBounds: true,
        findLabel: true,
        step: 1
    });

    showingDelayHandler.find('input').slideControl({
        fromMinMaxBounds: true,
        findLabel: true,
        step: 1
    });

    actionHandler.change(function(){
        Garlnd.App.setControls(actionHandler.val());
    });

    Garlnd.App.setControls(actionHandler.val());
});

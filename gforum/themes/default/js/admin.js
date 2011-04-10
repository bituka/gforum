Ext.ns('org.gforum.i18n','org.gforum.admin');

org.gforum.admin.forumPath = '';

org.gforum.admin.hideGlobalLoadingMask = function() {
    Ext.get('loading').remove();
    Ext.fly('loading-mask').fadeOut({
        remove:true
    });
}; 

Ext.onReady(function() {
    Ext.QuickTips.init();
    org.gforum.admin.buildAdminScreen();
    org.gforum.admin.hideGlobalLoadingMask.defer(150);
});

org.gforum.admin.buildAdminScreen = function() {

    //
    // data for Forums Grid
    //
    var forumsStore = new Ext.data.JsonStore({
        autoDestroy: true,
        autoLoad:    true,
        storeId: 'forumsStore',
        root: 'data',
        idProperty: 'key',
        proxy: new Ext.data.HttpProxy({
            url: String.format('{0}/api/v1/admin/forums',org.gforum.admin.forumPath),
            method: 'GET'
        }),
        fields: [
            'id','key','name','permalink', 'create_date', 'messages_number', 'threads_number'
        ]
    });
    
    var mainPanel = new Ext.TabPanel({
        renderTo: 'mainPanelDiv',
        activeTab: 0,
        flex: 1,
        width:window.innerWidth-20,
        height: window.innerHeight-100,
        frame: false,
        plain:true,
        defaults: {autoScroll: true},
        items:[{
                id: 'tab-forums',
                xtype: 'container',
                title: 'Forums',
                layout: 'fit',
                items: {
                    id: 'forums-grid',
                    width: '100%',
                    xtype: 'grid',
                    store: forumsStore,
                    columns: [
                        { header: 'Name', width: 200,       dataIndex: 'name' },
                        { header: 'Permalink', width: 400,  dataIndex: 'permalink'},
                        { header: 'Create Date', width: 150, dataIndex: 'create_date' },
                        { header: 'Messages', width: 80,  dataIndex: 'messages_number'},
                        { header: 'Threads',  width: 80,  dataIndex: 'threads_number'}
                    ],
                    loadMask: { msg: 'Loading' },
                    listeners: {
                        rowdblclick: function(theGrid,theRowIndex,theEventObject) {
                            //var rec = applicationsGrid_store.getAt(theRowIndex);
                            //applicationFilesGrid_store.loadApplicationFiles(rec.get('id'));
                        }
                    },
                    tbar: new Ext.Toolbar({
                        defaults:{ margins:'5 5 5 5' },
                        items:[{
                            xtype:'button',
                            text: 'Create forum',
                            iconCls: 'addIcon16',
                            handler: function() {
                                org.gforum.admin.showCreateUpdateForumWindow();
                            }
                        },'->',{
                            xtype:'button',
                            text: 'Refresh',
                            iconCls: 'refreshIcon16',
                            handler: function() {
                                forumsStore.reload();
                            }
                        }]
                    })
                }                
            },{
                id: 'tab-users',
                xtype: 'container',
                title: 'Users',
                //layout: 'fit',
                html: 'users here'
            },{
                id: 'tab-images',
                xtype: 'container',
                title: 'Images',
                html: 'list of images here'
            },{
                id: 'tab-settings',
                xtype: 'container',
                title: 'Settings',
                html: 'settings here'
            }
        ]      
    });
}

org.gforum.admin.showCreateUpdateForumWindow = function(data) {
    if (!org.gforum.admin.createUpdateForumWindow) {
        org.gforum.admin.createUpdateForumWindow = new Ext.Window({
            resizable: false,
            width:380,
            height:210,
            closeAction:'hide',
            plain: true,
            layout: 'fit',

            items: new Ext.form.FormPanel({
                id: 'createForumWnd-form',
                border:false,
                bodyStyle:'padding:5px 5px 0',
                labelWidth: 70, 
                items: [{
                    xtype: 'textfield',
                    id: 'createForumWnd-name',
                    width: 270,
                    fieldLabel: 'Forum title',
                    allowBlank: false
                },{
                    xtype: 'textfield',
                    id: 'createForumWnd-permalink',
                    width: 270,
                    fieldLabel: 'Permalink',
                    allowBlank: false
                },{
                    xtype: 'textarea',
                    id: 'createForumWnd-description',
                    width: 270,
                    height: 60,
                    fieldLabel: 'Description'
                }]
            }),

            buttons: [{
                text: 'Cancel',
                iconCls: 'cancelIcon16',
                handler: function() {
                    org.gforum.admin.createUpdateForumWindow.hide();
                }
            },{
                text: 'Save',
                iconCls: 'saveIcon16',
                handler: function(){

                    if (!Ext.getCmp('createForumWnd-form').getForm().isValid()) return;

                    var data1 = {
                        name       : Ext.getCmp('createForumWnd-name').getValue(),
                        permalink  : Ext.getCmp('createForumWnd-permalink').getValue(),
                        description: Ext.getCmp('createForumWnd-description').getValue(),
                    };

                    var sendDataMask = new Ext.LoadMask(Ext.getBody(), {
                        msg: 'Send data...'
                    });

                    sendDataMask.show();

                    org.gforum.admin.sendCreateUpdateForumCommand(data1, function(data2) {
                        sendDataMask.hide();
                        if (!data2.success) {
                            //com.vsystems.showErrorWindow(null,data.message);
                        } else {
                            org.gforum.admin.createUpdateForumWindow.hide();
                            Ext.StoreMgr.lookup('forumsStore').reload();
                        }
                    });
                }
            }]
        });
    }
    
    if (data) {
        org.gforum.admin.createUpdateForumWindow.setTitle('Edit forum');
        
        Ext.getCmp('createForumWnd-name').setValue(data.name);
        Ext.getCmp('createForumWnd-permalink').setValue(data.permalink);
        Ext.getCmp('createForumWnd-description').setValue(data.description);
    } else {
        org.gforum.admin.createUpdateForumWindow.setTitle('Create forum');
    }

    org.gforum.admin.createUpdateForumWindow.show();
}

org.gforum.admin.sendCreateUpdateForumCommand = function(data, callbackFn) {
    Ext.Ajax.request({
        url: String.format('{0}/api/v1/admin/create_forum', org.gforum.admin.forumPath),
        params: {
            forum_name       : data.name,
            forum_permalink  : data.permalink,
            forum_description: data.description
        },
        callback: function(options, success, response) {
            var data = {
                success: false,
                message: 'Connection error'
            };
            
            if (success) {
                var r = Ext.util.JSON.decode(response.responseText);
                if (r.status != 'ok') {
                    data.message = r.errorMsg;
                } else {
                    data.success = true;
                    data.message = '';
                }
            }
            callbackFn.call(this, data);
        }
    });
}

var tmap = [];
tmap[' ']='_';
tmap['а']='a';
tmap['б']='b';
tmap['в']='v';
tmap['г']='g';
tmap['д']='d';
tmap['е']='e';
tmap['ё']='jo';
tmap['ж']='zh';
tmap['з']='z';
tmap['и']='i';
tmap['й']='jj';
tmap['к']='k';
tmap['л']='l';
tmap['м']='m';
tmap['н']='n';
tmap['о']='o';
tmap['п']='p';
tmap['р']='r';
tmap['с']='s';
tmap['т']='t';
tmap['у']='u';
tmap['ф']='f';
tmap['х']='kh';
tmap['ц']='ts';
tmap['ч']='ch';
tmap['ш']='sh';
tmap['щ']='shh';
tmap['ъ']='';
tmap['ы']='y';
tmap['ь']='';
tmap['э']='eh';
tmap['ю']='ju';
tmap['я']='ja';
tmap['А']='A';
tmap['Б']='B';
tmap['В']='V';
tmap['Г']='G';
tmap['Д']='D';
tmap['Е']='E';
tmap['Ё']='Jo';
tmap['Ж']='Zh';
tmap['З']='Z';
tmap['И']='I';
tmap['Й']='Jj';
tmap['К']='K';
tmap['Л']='L';
tmap['М']='M';
tmap['Н']='N';
tmap['О']='O';
tmap['П']='P';
tmap['Р']='R';
tmap['С']='S';
tmap['Т']='T';
tmap['У']='U';
tmap['Ф']='F';
tmap['Х']='Kh';
tmap['Ц']='C';
tmap['Ч']='Ch';
tmap['Ш']='Sh';
tmap['Щ']='Shh';
tmap['Ъ']='';
tmap['Ы']='Y';
tmap['Ь']='';
tmap['Э']='Eh';
tmap['Ю']='Ju';
tmap['Я']='Ja';

org.gforum.admin.translit = function(txt) {
    var txt1 = [];
    for (var i=0; i<txt.length; i++) {
        var c = tmap[txt.charAt(i)];
        if (c) txt1.push(c);
        else   txt1.push(txt.charAt(i));
    }
    return txt1.join('');
}

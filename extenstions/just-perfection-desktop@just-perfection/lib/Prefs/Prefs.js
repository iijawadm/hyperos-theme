/**
 * Prefs Library
 *
 * @author     Javad Rahmatzadeh <j.rahmatzadeh@gmail.com>
 * @copyright  2020-2024
 * @license    GPL-3.0-only
 */

/**
 * prefs widget for showing prefs window
 */
export class Prefs
{
    /**
     * Current shell version
     *
     * @type {number|null}
     */
    #shellVersion = null;

    /**
     * Instance of PrefsKeys
     *
     * @type {PrefsKeys|null}
     */
    #prefsKeys = null;

    /**
     * Instance of Gtk.Builder
     *
     * @type {Gtk.Builder|null}
     */
    #builder = null;

    /**
     * Instance of Gio.Settings
     *
     * @type {Settings|null}
     */
    #settings = null;

    /**
     * Instance of Gdk
     *
     * @type {Gdk|null}
     */
    #gdk = null;

    /**
     * All available profile names
     *
     * @type {Array}
     */
    #profiles = [
        'default',
        'minimal',
        'superminimal',
    ];

    /**
     * class constructor
     *
     * @param {Object} dependencies
     *   'Builder' instance of Gtk::Builder
     *   'Settings' instance of Gio::Settings
     *   'Gdk' reference to Gdk
     *   'GLib' reference to GLib
     * @param {PrefsKeys.PrefsKeys} prefsKeys instance of PrefsKeys
     * @param {number} shellVersion float in major.minor format
     */
    constructor(dependencies, prefsKeys, shellVersion)
    {
        this.#settings = dependencies['Settings'] || null;
        this.#builder = dependencies['Builder'] || null;
        this.#gdk = dependencies['Gdk'] || null;

        this.#prefsKeys = prefsKeys;
        this.#shellVersion = shellVersion;
    }

    /**
     * fill prefs window
     *
     * @param {string} UIFolderPath folder path to ui folder
     * @param {string} gettextDomain gettext domain
     *
     * @returns {void}
     */
     fillPrefsWindow(window, UIFolderPath, gettextDomain)
     {
         // changing the order here can change the elements order in ui 
         let uiFilenames = [
             'profile',
             'visibility',
             'icons',
             'behavior',
             'customize',
         ];
 
         this.#builder.set_translation_domain(gettextDomain);
         for (let uiFilename of uiFilenames) {
             this.#builder.add_from_file(`${UIFolderPath}/adw/${uiFilename}.ui`);
         }

         for (let uiFilename of uiFilenames) {
             let page = this.#builder.get_object(uiFilename);
             window.add(page);
         }
 
         this.#setValues();
         this.#guessProfile();
         this.#onlyShowSupportedRows();
         this.#registerAllSignals(window);

         this.#setWindowSize(window);

         window.search_enabled = true;
     }

    /**
     * set window size
     *
     * @param {Adw.PreferencesWindow} window prefs window
     *
     * @returns {void}
     */
    #setWindowSize(window)
    {
        let [pmWidth, pmHeight, pmScale] = this.#getPrimaryMonitorInfo();
        let sizeTolerance = 50;
        let width = 600;
        let height = 650;

        if (
            (pmWidth / pmScale) - sizeTolerance >= width &&
            (pmHeight / pmScale) - sizeTolerance >= height
        ) {
            window.set_default_size(width, height);
        }
    }

    /**
     * get primary monitor info
     *
     * @returns {Array} [width, height, scale]
     */
    #getPrimaryMonitorInfo()
    {
        let display = this.#gdk.Display.get_default();

        let pm = display.get_monitors().get_item(0);

        if (!pm) {
            return [700, 500, 1];
        }

        let geo = pm.get_geometry();
        let scale = pm.get_scale_factor();

        return [geo.width, geo.height, scale];
    }

    /**
     * register all signals
     *
     * @param {Adw.PreferencesWindow} window prefs dialog
     *
     * @returns {void}
     */
    #registerAllSignals(window)
    {
        this.#registerKeySignals();
        this.#registerProfileSignals();
    }

    /**
     * register signals of all prefs keys
     *
     * @returns {void}
     */
     #registerKeySignals()
     {
         // all available keys
         for (let [, key] of Object.entries(this.#prefsKeys.keys)) {
 
             switch (key.widgetType) {
 
                 case 'GtkSwitch':
                     this.#builder.get_object(key.widgetId).connect('state-set', (w) => {
                         this.#settings.set_boolean(key.name, w.get_active());
                         this.#guessProfile();
                     });
                     break;
 
                 case 'AdwActionRow':
                     this.#builder.get_object(key.widgetId).connect('notify::selected-item', (w) => {
                         let index = w.get_selected();
                         let value = (index in key.maps) ? key.maps[index] : index; 
                         this.#settings.set_int(key.name, value);
                         this.#guessProfile();
                     });
                     break;
             }
         }
    }

    /**
     * register profile signals
     *
     * @returns {void}
     */
    #registerProfileSignals()
    {
        for (let profile of this.#profiles) {
            let widget = this.#builder.get_object(`profile_${profile}`);
            if (!widget) {
                break;
            }
            widget.connect('clicked', (w) => {
                this.#setValues(profile);
            });
        }
    }

    /**
     * can check all current values and guess the profile based on the values
     *
     * @returns {void}
     */
    #guessProfile()
    {
        let totalCount = 0;
        let matchCount = {};

        for (let profile of this.#profiles) {
            matchCount[profile] = 0;
        }

        for (let [, key] of Object.entries(this.#prefsKeys.keys)) {
        
            if (!key.supported) {
                continue;
            }

            let value;

            switch (key.widgetType) {
                case 'GtkSwitch':
                    value = this.#builder.get_object(key.widgetId).get_active();
                    break;
                case 'AdwActionRow':
                    value = this.#builder.get_object(key.widgetId).get_selected();
                    break;
                default:
                    value = '';
                    continue;
            }
            
            for (let profile of this.#profiles) {
                if (key.profiles[profile] === value) {
                    matchCount[profile]++;
                }
            }

            totalCount++;
        }

        let currentProfile = 'custom';
        for (let profile of this.#profiles) {
            if (matchCount[profile] === totalCount) {
                currentProfile = profile;
                break;
            }
        }
        
        let widget = this.#builder.get_object(`profile_${currentProfile}`);
        if (widget) {
            widget.set_active(true);
        }
    }

    /**
     * set values for all elements
     *
     * @param {string} profile profile name or null for get it from gsettings
     *
     * @returns {void}
     */
    #setValues(profile)
    {
        for (let [, key] of Object.entries(this.#prefsKeys.keys)) {

            let widget = this.#builder.get_object(key.widgetId);

            switch (key.widgetType) {

                case 'GtkSwitch':
                    let value
                    = (profile)
                    ? key.profiles[profile]
                    : this.#settings.get_boolean(key.name);

                    widget.set_active(value);
                    break;

                case 'AdwActionRow':
                    let index
                    = (profile)
                    ? key.profiles[profile]
                    : this.#settings.get_int(key.name);

                    for (let k in key.maps) {
                        if (key.maps[k] === index) {
                            index = k;
                            break;
                        }
                    }
                    widget.set_selected(index);
                    break;
            }
        }
    }

    /**
     * apply all supported keys to the elements
     *
     * @returns {void}
     */
     #onlyShowSupportedRows()
     {
         for (let [, key] of Object.entries(this.#prefsKeys.keys)) {
            let row = this.#builder.get_object(`${key.id}_row`);
            let visible = key.supported;
            row.visible = visible;
        }
     }
};


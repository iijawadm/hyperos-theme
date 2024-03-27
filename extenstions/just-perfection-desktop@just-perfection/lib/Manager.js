/**
 * Manager Library
 *
 * @author     Javad Rahmatzadeh <j.rahmatzadeh@gmail.com>
 * @copyright  2020-2024
 * @license    GPL-3.0-only
 */

/**
 * Apply settings to the GNOME Shell
 */
export class Manager
{
    /**
     * Current shell version
     *
     * @type {number|null}
     */
    #shellVersion = null;

    /**
     * Instance of API
     *
     * @type {API|null}
     */
    #api = null;

    /**
     * Instance of Gio.Settings
     *
     * @type {Settings|null}
     */
    #settings = null;

    /**
     * Class Constructor
     *
     * @param {Object} dependencies
     *   'API' instance of lib::API
     *   'Settings' instance of Gio::Settings
     * @param {number} shellVersion float in major.minor format
     */
    constructor(dependencies, shellVersion)
    {
        this.#api = dependencies['API'] || null;
        this.#settings = dependencies['Settings'] || null;

        this.#shellVersion = shellVersion;
    }

    /**
     * register all signals for settings
     *
     * @returns {void}
     */
    registerSettingsSignals()
    {
        this.#settings.connect('changed::panel', () => {
            this.#applyPanel(false);
        });

        this.#settings.connect('changed::panel-in-overview', () => {
            this.#applyPanel(false);
        });

        this.#settings.connect('changed::search', () => {
            this.#applySearch(false);
        });

        this.#settings.connect('changed::dash', () => {
            this.#applyDash(false);
        });

        this.#settings.connect('changed::osd', () => {
            this.#applyOSD(false);
        });

        this.#settings.connect('changed::workspace-popup', () => {
            this.#applyWorkspacePopup(false);
        });

        this.#settings.connect('changed::workspace', () => {
            this.#applyWorkspace(false);
        });

        this.#settings.connect('changed::background-menu', () => {
            this.#applyBackgroundMenu(false);
        });

        this.#settings.connect('changed::theme', () => {
            this.#applyTheme(false);
        });

        this.#settings.connect('changed::activities-button', () => {
            this.#applyActivitiesButton(false);
        });

        this.#settings.connect('changed::clock-menu', () => {
            this.#applyClockMenu(false);
        });

        this.#settings.connect('changed::keyboard-layout', () => {
            this.#applyKeyboardLayout(false);
        });

        this.#settings.connect('changed::accessibility-menu', () => {
            this.#applyAccessibilityMenu(false);
        });

        this.#settings.connect('changed::quick-settings', () => {
            this.#applyQuickSettings(false);
        });

        this.#settings.connect('changed::window-picker-icon', () => {
            this.#applyWindowPickerIcon(false);
        });

        this.#settings.connect('changed::type-to-search', () => {
            this.#applyTypeToSearch(false);
        });

        this.#settings.connect('changed::workspace-switcher-size', () => {
            this.#applyWorkspaceSwitcherSize(false);
        });

        this.#settings.connect('changed::power-icon', () => {
            this.#applyPowerIcon(false);
        });

        this.#settings.connect('changed::top-panel-position', () => {
            this.#applyTopPanelPosition(false);
        });

        this.#settings.connect('changed::panel-notification-icon', () => {
            this.#applyPanelNotificationIcon(false);
        });

        this.#settings.connect('changed::clock-menu-position', () => {
            this.#applyClockMenuPosition(false);
        });

        this.#settings.connect('changed::clock-menu-position-offset', () => {
            this.#applyClockMenuPosition(false);
        });

        this.#settings.connect('changed::show-apps-button', () => {
            this.#applyShowAppsButton(false);
        });

        this.#settings.connect('changed::animation', () => {
            this.#applyAnimation(false);
        });

        this.#settings.connect('changed::window-demands-attention-focus', () => {
            this.#applyWindowDemandsAttentionFocus(false);
        });

        this.#settings.connect('changed::window-maximized-on-create', () => {
            this.#applyWindowMaximizedOnCreate(false);
        });

        this.#settings.connect('changed::dash-icon-size', () => {
            this.#applyDashIconSize(false);
        });

        this.#settings.connect('changed::startup-status', () => {
            this.#applyStartupStatus(false);
        });

        this.#settings.connect('changed::workspaces-in-app-grid', () => {
            this.#applyWorkspacesInAppGrid(false);
        });

        this.#settings.connect('changed::notification-banner-position', () => {
            this.#applyNotificationBannerPosition(false);
        });

        this.#settings.connect('changed::workspace-switcher-should-show', () => {
            this.#applyWorkspaceSwitcherShouldShow(false);
        });

        this.#settings.connect('changed::panel-size', () => {
            this.#applyPanelSize(false);
        });

        this.#settings.connect('changed::panel-button-padding-size', () => {
            this.#applyPanelButtonPaddingSize(false);
        });

        this.#settings.connect('changed::panel-indicator-padding-size', () => {
            this.#applyPanelIndicatorPaddingSize(false);
        });

        this.#settings.connect('changed::window-preview-caption', () => {
            this.#applyWindowPreviewCaption(false);
        });

        this.#settings.connect('changed::window-preview-close-button', () => {
            this.#applyWindowPreviewCloseButton(false);
        });

        this.#settings.connect('changed::workspace-background-corner-size', () => {
            this.#applyWorkspaceBackgroundCornerSize(false);
        });

        this.#settings.connect('changed::workspace-wrap-around', () => {
            this.#applyWorkspaceWrapAround(false);
        });

        this.#settings.connect('changed::ripple-box', () => {
            this.#applyRippleBox(false);
        });

        this.#settings.connect('changed::overlay-key', () => {
            this.#applyOverlayKey(false);
        });

        this.#settings.connect('changed::double-super-to-appgrid', () => {
            this.#applyOverlayKey(false);
        });

        this.#settings.connect('changed::switcher-popup-delay', () => {
            this.#applySwitcherPopupDelay(false);
        });

        this.#settings.connect('changed::world-clock', () => {
            this.#applyWorldClock(false);
        });

        this.#settings.connect('changed::weather', () => {
            this.#applyWeather(false);
        });

        this.#settings.connect('changed::calendar', () => {
            this.#applyCalendar(false);
        });

        this.#settings.connect('changed::events-button', () => {
            this.#applyEventsButton(false);
        });

        this.#settings.connect('changed::panel-icon-size', () => {
            this.#applyPanelIconSize(false);
        });

        this.#settings.connect('changed::dash-separator', () => {
            this.#applyDashSeparator(false);
        });

        this.#settings.connect('changed::looking-glass-width', () => {
            this.#applyLookingGlassSize(false);
        });

        this.#settings.connect('changed::looking-glass-height', () => {
            this.#applyLookingGlassSize(false);
        });

        this.#settings.connect('changed::osd-position', () => {
            this.#applyOSDPosition(false);
        });

        this.#settings.connect('changed::window-menu-take-screenshot-button', () => {
            this.#applyWindowMenuTakeScreenshotButton(false);
        });

        this.#settings.connect('changed::alt-tab-window-preview-size', () => {
            this.#applyAltTabWindowPreviewSize(false);
        });

        this.#settings.connect('changed::alt-tab-small-icon-size', () => {
            this.#applyAltTabSmallIconSize(false);
        });

        this.#settings.connect('changed::alt-tab-icon-size', () => {
            this.#applyAltTabIconSize(false);
        });

        this.#settings.connect('changed::screen-sharing-indicator', () => {
            this.#applyScreenSharingIndicator(false);
        });
        
        this.#settings.connect('changed::screen-recording-indicator', () => {
            this.#applyScreenRecordingIndicator(false);
        });

        this.#settings.connect('changed::controls-manager-spacing-size', () => {
            this.#applyControlsManagerSpacingSize(false);
        });

        this.#settings.connect('changed::workspace-peek', () => {
            this.#applyWorkspacePeek(false);
        });

        this.#settings.connect('changed::dash-app-running', () => {
            this.#applyDashAppRunning(true);
        });
    }

    /**
     * apply everything to the GNOME Shell
     *
     * @returns {void}
     */
    applyAll()
    {
        this.#applyTheme(false);
        this.#applyPanel(false);
        this.#applySearch(false);
        this.#applyDash(false);
        this.#applyOSD(false);
        this.#applyWorkspacePopup(false);
        this.#applyWorkspace(false);
        this.#applyBackgroundMenu(false);
        this.#applyActivitiesButton(false);
        this.#applyClockMenu(false);
        this.#applyKeyboardLayout(false);
        this.#applyAccessibilityMenu(false);
        this.#applyQuickSettings(false);
        this.#applyWindowPickerIcon(false);
        this.#applyTypeToSearch(false);
        this.#applyWorkspaceSwitcherSize(false);
        this.#applyPowerIcon(false);
        this.#applyTopPanelPosition(false);
        this.#applyPanelNotificationIcon(false);
        this.#applyClockMenuPosition(false);
        this.#applyShowAppsButton(false);
        this.#applyAnimation(false);
        this.#applyWindowDemandsAttentionFocus(false);
        this.#applyWindowMaximizedOnCreate(false);
        this.#applyDashIconSize(false);
        this.#applyStartupStatus(false);
        this.#applyWorkspacesInAppGrid(false);
        this.#applyNotificationBannerPosition(false);
        this.#applyWorkspaceSwitcherShouldShow(false);
        this.#applyPanelSize(false);
        this.#applyPanelButtonPaddingSize(false);
        this.#applyPanelIndicatorPaddingSize(false);
        this.#applyWindowPreviewCaption(false);
        this.#applyWindowPreviewCloseButton(false);
        this.#applyWorkspaceBackgroundCornerSize(false);
        this.#applyWorkspaceWrapAround(false);
        this.#applyRippleBox(false);
        this.#applyOverlayKey(false);
        this.#applySwitcherPopupDelay(false);
        this.#applyWorldClock(false);
        this.#applyWeather(false);
        this.#applyPanelIconSize(false);
        this.#applyEventsButton(false);
        this.#applyCalendar(false);
        this.#applyDashSeparator(false);
        this.#applyLookingGlassSize(false);
        this.#applyOSDPosition(false);
        this.#applyWindowMenuTakeScreenshotButton(false);
        this.#applyAltTabWindowPreviewSize(false);
        this.#applyAltTabSmallIconSize(false);
        this.#applyAltTabIconSize(false);
        this.#applyScreenSharingIndicator(false);
        this.#applyScreenRecordingIndicator(false);
        this.#applyControlsManagerSpacingSize(false);
        this.#applyWorkspacePeek(false);
        this.#applyDashAppRunning(false);
    }

    /**
     * revert everything done by this class to the GNOME Shell
     *
     * @returns {void}
     */
    revertAll()
    {
        this.#applyTheme(true);
        this.#applyPanel(true);
        this.#applySearch(true);
        this.#applyDash(true);
        this.#applyOSD(true);
        this.#applyWorkspace(true);
        this.#applyWorkspacePopup(true);
        this.#applyBackgroundMenu(true);
        this.#applyActivitiesButton(true);
        this.#applyClockMenu(true);
        this.#applyKeyboardLayout(true);
        this.#applyAccessibilityMenu(true);
        this.#applyQuickSettings(true);
        this.#applyWindowPickerIcon(true);
        this.#applyTypeToSearch(true);
        this.#applyWorkspaceSwitcherSize(true);
        this.#applyPowerIcon(true);
        this.#applyTopPanelPosition(true);
        this.#applyPanelNotificationIcon(true);
        this.#applyClockMenuPosition(true);
        this.#applyShowAppsButton(true);
        this.#applyAnimation(true);
        this.#applyWindowDemandsAttentionFocus(true);
        this.#applyWindowMaximizedOnCreate(true);
        this.#applyDashIconSize(true);
        this.#applyStartupStatus(true);
        this.#applyWorkspacesInAppGrid(true);
        this.#applyNotificationBannerPosition(true);
        this.#applyWorkspaceSwitcherShouldShow(true);
        this.#applyPanelSize(true);
        this.#applyPanelButtonPaddingSize(true);
        this.#applyPanelIndicatorPaddingSize(true);
        this.#applyWindowPreviewCaption(true);
        this.#applyWindowPreviewCloseButton(true);
        this.#applyWorkspaceBackgroundCornerSize(true);
        this.#applyWorkspaceWrapAround(true);
        this.#applyRippleBox(true);
        this.#applyOverlayKey(true);
        this.#applySwitcherPopupDelay(true);
        this.#applyWorldClock(true);
        this.#applyWeather(true);
        this.#applyPanelIconSize(true);
        this.#applyEventsButton(true);
        this.#applyCalendar(true);
        this.#applyDashSeparator(true);
        this.#applyLookingGlassSize(true);
        this.#applyOSDPosition(true);
        this.#applyWindowMenuTakeScreenshotButton(true);
        this.#applyAltTabWindowPreviewSize(true);
        this.#applyAltTabSmallIconSize(true);
        this.#applyAltTabIconSize(true);
        this.#applyScreenSharingIndicator(true);
        this.#applyScreenRecordingIndicator(true);
        this.#applyControlsManagerSpacingSize(true);
        this.#applyWorkspacePeek(true);
        this.#applyDashAppRunning(true);
    }

    /**
     * apply panel settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyPanel(forceOriginal)
    {
        let panel = this.#settings.get_boolean('panel');
        let panelInOverview = this.#settings.get_boolean('panel-in-overview');

        if (forceOriginal || panel) {
            this.#api.panelShow();
        } else {
            let mode = (panelInOverview) ? 1 : 0;
            this.#api.panelHide(mode);
        }
    }

    /**
     * apply search settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applySearch(forceOriginal)
    {
        if (forceOriginal || this.#settings.get_boolean('search')) {
            this.#api.searchEntryShow(false);
        } else {
            this.#api.searchEntryHide(false);
        }
    }

    /**
     * apply type to search settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyTypeToSearch(forceOriginal)
    {
        if (forceOriginal || this.#settings.get_boolean('type-to-search')) {
            this.#api.startSearchEnable();
        } else {
            this.#api.startSearchDisable();
        }
    }

    /**
     * apply dash settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyDash(forceOriginal)
    {
        if (forceOriginal || this.#settings.get_boolean('dash')) {
            this.#api.dashShow();
        } else {
            this.#api.dashHide();
        }
    }

    /**
     * apply osd settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyOSD(forceOriginal)
    {
        if (forceOriginal || this.#settings.get_boolean('osd')) {
            this.#api.OSDEnable();
        } else {
            this.#api.OSDDisable();
        }
    }

    /**
     * apply workspace popup settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyWorkspacePopup(forceOriginal)
    {
        if (forceOriginal || this.#settings.get_boolean('workspace-popup')) {
            this.#api.workspacePopupEnable();
        } else {
            this.#api.workspacePopupDisable();
        }
    }

    /**
     * apply workspace settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyWorkspace(forceOriginal)
    {
        if (forceOriginal || this.#settings.get_boolean('workspace')) {
            this.#api.workspaceSwitcherShow();
        } else {
            this.#api.workspaceSwitcherHide();
        }
    }

    /**
     * apply background menu settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyBackgroundMenu(forceOriginal)
    {
        if (forceOriginal || this.#settings.get_boolean('background-menu')) {
            this.#api.backgroundMenuEnable();
        } else {
            this.#api.backgroundMenuDisable();
        }
    }

    /**
     * apply theme settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyTheme(forceOriginal)
    {
        let className = 'just-perfection';

        if (forceOriginal || !this.#settings.get_boolean('theme')) {
            this.#api.UIStyleClassRemove(className);
        } else {
            this.#api.UIStyleClassAdd(className);
        }
    }

    /**
     * apply activities button settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyActivitiesButton(forceOriginal)
    {
        if (forceOriginal || this.#settings.get_boolean('activities-button')) {
            this.#api.activitiesButtonShow();
        } else {
            this.#api.activitiesButtonHide();
        }
    }

    /**
     * apply clock menu (aka date menu) settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyClockMenu(forceOriginal)
    {
        if (forceOriginal || this.#settings.get_boolean('clock-menu')) {
            this.#api.dateMenuShow();
        } else {
            this.#api.dateMenuHide();
        }
    }

    /**
     * apply keyboard layout settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyKeyboardLayout(forceOriginal)
    {
        if (forceOriginal || this.#settings.get_boolean('keyboard-layout')) {
            this.#api.keyboardLayoutShow();
        } else {
            this.#api.keyboardLayoutHide();
        }
    }

    /**
     * apply accessibility menu settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyAccessibilityMenu(forceOriginal)
    {
        if (forceOriginal || this.#settings.get_boolean('accessibility-menu')) {
            this.#api.accessibilityMenuShow();
        } else {
            this.#api.accessibilityMenuHide();
        }
    }

    /**
     * apply quick settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyQuickSettings(forceOriginal)
    {
        if (forceOriginal || this.#settings.get_boolean('quick-settings')) {
            this.#api.quickSettingsMenuShow();
        } else {
            this.#api.quickSettingsMenuHide();
        }
    }

    /**
     * apply window picker icon settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyWindowPickerIcon(forceOriginal)
    {
        if (forceOriginal || this.#settings.get_boolean('window-picker-icon')) {
            this.#api.windowPickerIconEnable();
        } else {
            this.#api.windowPickerIconDisable();
        }
    }

    /**
     * apply workspace switcher size settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyWorkspaceSwitcherSize(forceOriginal)
    {
        let size = this.#settings.get_int('workspace-switcher-size');

        if (forceOriginal || size === 0) {
            this.#api.workspaceSwitcherSetDefaultSize();
        } else {
            this.#api.workspaceSwitcherSetSize(size / 100);
        }
    }

    /**
     * apply power icon settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyPowerIcon(forceOriginal)
    {
        if (forceOriginal || this.#settings.get_boolean('power-icon')) {
            this.#api.powerIconShow();
        } else {
            this.#api.powerIconHide();
        }
    }

    /**
     * apply top panel position settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyTopPanelPosition(forceOriginal)
    {
        if (forceOriginal || this.#settings.get_int('top-panel-position') === 0) {
            this.#api.panelSetPosition(0);
        } else {
            this.#api.panelSetPosition(1);
        }
    }

    /**
     * apply panel notification icon settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyPanelNotificationIcon(forceOriginal)
    {
        if (forceOriginal || this.#settings.get_boolean('panel-notification-icon')) {
            this.#api.panelNotificationIconEnable();
        } else {
            this.#api.panelNotificationIconDisable();
        }
    }

    /**
     * apply clock menu position settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyClockMenuPosition(forceOriginal)
    {
        if (forceOriginal) {
            this.#api.clockMenuPositionSetDefault();
        } else {
            let pos = this.#settings.get_int('clock-menu-position');
            let offset = this.#settings.get_int('clock-menu-position-offset');
            this.#api.clockMenuPositionSet(pos, offset);
        }
    }

    /**
     * apply show apps button settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyShowAppsButton(forceOriginal)
    {
        if (forceOriginal || this.#settings.get_boolean('show-apps-button')) {
            this.#api.showAppsButtonEnable();
        } else {
            this.#api.showAppsButtonDisable();
        }
    }

    /**
     * apply animation settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyAnimation(forceOriginal)
    {
        let animation = this.#settings.get_int('animation');

        let factors = [
            0.01, // almost none
            0.2, // fastest
            0.6, // faster
            0.8, // fast
            1.3, // slow
            1.6, // slower
            2.8, // slowest
        ];

        if (forceOriginal) {
            this.#api.animationSpeedSetDefault();
            this.#api.enableAnimationsSetDefault();
        } else if (animation === 0) {
            // disabled
            this.#api.animationSpeedSetDefault();
            this.#api.enableAnimationsSet(false);
        } else if (animation === 1) {
            // default speed
            this.#api.animationSpeedSetDefault();
            this.#api.enableAnimationsSet(true);
        } else if (factors[animation - 2] !== undefined) {
            // custom speed
            this.#api.animationSpeedSet(factors[animation - 2]);
            this.#api.enableAnimationsSet(true);
        }
    }

    /**
     * apply window demands attention focus settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyWindowDemandsAttentionFocus(forceOriginal)
    {
        let focus = this.#settings.get_boolean('window-demands-attention-focus');

        if (forceOriginal || !focus) {
            this.#api.windowDemandsAttentionFocusDisable();
        } else {
            this.#api.windowDemandsAttentionFocusEnable();
        }
    }

    /**
     * apply window maximized on create settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyWindowMaximizedOnCreate(forceOriginal)
    {
        let maximize = this.#settings.get_boolean('window-maximized-on-create');

        if (forceOriginal || !maximize) {
            this.#api.windowMaximizedOnCreateDisable();
        } else {
            this.#api.windowMaximizedOnCreateEnable();
        }
    }

    /**
     * apply dash icon size settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyDashIconSize(forceOriginal)
    {
        let size = this.#settings.get_int('dash-icon-size');

        if (forceOriginal || size === 0) {
            this.#api.dashIconSizeSetDefault();
        } else {
            this.#api.dashIconSizeSet(size);
        }
    }

    /**
     * apply startup status settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyStartupStatus(forceOriginal)
    {
        let status = this.#settings.get_int('startup-status');

        if (forceOriginal) {
            this.#api.startupStatusSetDefault();
        } else {
            this.#api.startupStatusSet(status);
        }
    }

    /**
     * apply workspaces in app grid status settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyWorkspacesInAppGrid(forceOriginal)
    {
        let status = this.#settings.get_boolean('workspaces-in-app-grid');

        if (forceOriginal || status) {
            this.#api.workspacesInAppGridEnable();
        } else {
            this.#api.workspacesInAppGridDisable();
        }
    }

    /**
     * apply notification banner position settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyNotificationBannerPosition(forceOriginal)
    {
        let pos = this.#settings.get_int('notification-banner-position');

        if (forceOriginal) {
            this.#api.notificationBannerPositionSetDefault();
        } else {
            this.#api.notificationBannerPositionSet(pos);
        }
    }

    /**
     * apply workspace switcher should show settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyWorkspaceSwitcherShouldShow(forceOriginal)
    {
        let shouldShow = this.#settings.get_boolean('workspace-switcher-should-show');

        if (forceOriginal || !shouldShow) {
            this.#api.workspaceSwitcherShouldShowSetDefault();
        } else {
            this.#api.workspaceSwitcherShouldShow(true);
        }
    }

    /**
     * apply panel size settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyPanelSize(forceOriginal)
    {
        let size = this.#settings.get_int('panel-size');

        if (forceOriginal || size === 0) {
            this.#api.panelSetDefaultSize();
        } else {
            this.#api.panelSetSize(size, false);
        }
    }

    /**
     * apply panel button padding size settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyPanelButtonPaddingSize(forceOriginal)
    {
        let size = this.#settings.get_int('panel-button-padding-size');

        if (forceOriginal || size === 0) {
            this.#api.panelButtonHpaddingSetDefault();
        } else {
            this.#api.panelButtonHpaddingSizeSet(size - 1);
        }
    }

    /**
     * apply panel indicator padding size settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyPanelIndicatorPaddingSize(forceOriginal)
    {
        let size = this.#settings.get_int('panel-indicator-padding-size');

        if (forceOriginal || size === 0) {
            this.#api.panelIndicatorPaddingSetDefault();
        } else {
            this.#api.panelIndicatorPaddingSizeSet(size - 1);
        }
    }

    /**
     * apply window preview caption settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyWindowPreviewCaption(forceOriginal)
    {
        let status = this.#settings.get_boolean('window-preview-caption');

        if (forceOriginal || status) {
            this.#api.windowPreviewCaptionEnable();
        } else {
            this.#api.windowPreviewCaptionDisable();
        }
    }

    /**
     * apply window preview close button settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyWindowPreviewCloseButton(forceOriginal)
    {
        let status = this.#settings.get_boolean('window-preview-close-button');

        if (forceOriginal || status) {
            this.#api.windowPreviewCloseButtonEnable();
        } else {
            this.#api.windowPreviewCloseButtonDisable();
        }
    }

    /**
     * apply workspace background corner size settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyWorkspaceBackgroundCornerSize(forceOriginal)
    {
        let size = this.#settings.get_int('workspace-background-corner-size');

        if (forceOriginal || size === 0) {
            this.#api.workspaceBackgroundRadiusSetDefault();
        } else {
            this.#api.workspaceBackgroundRadiusSet(size - 1);
        }
    }

    /**
     * apply workspace wrap around settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyWorkspaceWrapAround(forceOriginal)
    {
        let status = this.#settings.get_boolean('workspace-wrap-around');

        if (forceOriginal || !status) {
            this.#api.workspaceWraparoundDisable();
        } else {
            this.#api.workspaceWraparoundEnable();
        }
    }
    
    /**
     * apply ripple box settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyRippleBox(forceOriginal)
    {
        let status = this.#settings.get_boolean('ripple-box');

        if (forceOriginal || status) {
            this.#api.rippleBoxEnable();
        } else {
            this.#api.rippleBoxDisable();
        }
    }

    /**
     * apply overlay key
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyOverlayKey(forceOriginal)
    {
        let overlayKey = this.#settings.get_boolean('overlay-key');
        let doubleSuper = this.#settings.get_boolean('double-super-to-appgrid');

        if (forceOriginal) {
            this.#api.doubleSuperToAppGridEnable();
            this.#api.unblockOverlayKey();
        } else if (!overlayKey) {
            this.#api.doubleSuperToAppGridEnable();
            this.#api.blockOverlayKey();
        } else {
            this.#api.unblockOverlayKey();
            if (doubleSuper) {
                this.#api.doubleSuperToAppGridEnable();
            } else {
                this.#api.doubleSuperToAppGridDisable();
            }
        }
    }

    /**
     * apply switcher popup delay settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applySwitcherPopupDelay(forceOriginal)
    {
        let status = this.#settings.get_boolean('switcher-popup-delay');

        if (forceOriginal || status) {
            this.#api.switcherPopupDelaySetDefault();
        } else {
            this.#api.removeSwitcherPopupDelay();
        }
    }

    /**
     * apply world clock settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyWorldClock(forceOriginal)
    {
        let status = this.#settings.get_boolean('world-clock');

        if (forceOriginal || status) {
            this.#api.worldClocksShow();
        } else {
            this.#api.worldClocksHide();
        }
    }

    /**
     * apply weather settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyWeather(forceOriginal)
    {
        let status = this.#settings.get_boolean('weather');

        if (forceOriginal || status) {
            this.#api.weatherShow();
        } else {
            this.#api.weatherHide();
        }
    }

    /**
     * apply calendar settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyCalendar(forceOriginal)
    {
        let status = this.#settings.get_boolean('calendar');

        if (forceOriginal || status) {
            this.#api.calendarShow();
        } else {
            this.#api.calendarHide();
        }
    }

    /**
     * apply events button settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyEventsButton(forceOriginal)
    {
        let status = this.#settings.get_boolean('events-button');

        if (forceOriginal || status) {
            this.#api.eventsButtonShow();
        } else {
            this.#api.eventsButtonHide();
        }
    }

    /**
     * apply panel icon size settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyPanelIconSize(forceOriginal)
    {
        let size = this.#settings.get_int('panel-icon-size');

        if (forceOriginal || size === 0) {
            this.#api.panelIconSetDefaultSize();
        } else {
            this.#api.panelIconSetSize(size);
        }
    }

    /**
     * apply dash separator settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyDashSeparator(forceOriginal)
    {
        let status = this.#settings.get_boolean('dash-separator');

        if (forceOriginal || status) {
            this.#api.dashSeparatorShow();
        } else {
            this.#api.dashSeparatorHide();
        }
    }

    /**
     * apply looking glass size settings
     * 
     * @param {boolean} forceOriginal force original shell setting
     * 
     * @returns {void}
     */
    #applyLookingGlassSize(forceOriginal)
    {
        let widthSize = this.#settings.get_int('looking-glass-width');
        let heightSize = this.#settings.get_int('looking-glass-height');

        if (forceOriginal) {
            this.#api.lookingGlassSetDefaultSize();
        } else {
            let width = (widthSize !== 0) ? widthSize / 10 : null;
            let height = (heightSize !== 0) ? heightSize / 10 : null;
            this.#api.lookingGlassSetSize(width, height);
        }
    }

    /**
     * apply osd position settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyOSDPosition(forceOriginal)
    {
        let pos = this.#settings.get_int('osd-position');

        if (forceOriginal || pos === 0) {
            this.#api.osdPositionSetDefault();
        } else {
            this.#api.osdPositionSet(pos - 1);
        }
    }
    
    /**
     * apply window menu take screenshot button settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyWindowMenuTakeScreenshotButton(forceOriginal)
    {
        let status = this.#settings.get_boolean('window-menu-take-screenshot-button');

        if (forceOriginal || status) {
            this.#api.screenshotInWindowMenuShow();
        } else {
            this.#api.screenshotInWindowMenuHide();
        }
    }

    /**
     * apply alt tab window preview size settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyAltTabWindowPreviewSize(forceOriginal)
    {
        let size = this.#settings.get_int('alt-tab-window-preview-size');

        if (forceOriginal || size === 0) {
            this.#api.altTabWindowPreviewSetDefaultSize();
        } else {
            this.#api.altTabWindowPreviewSetSize(size);
        }
    }

    /**
     * apply alt tab small icon size settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyAltTabSmallIconSize(forceOriginal)
    {
        let size = this.#settings.get_int('alt-tab-small-icon-size');

        if (forceOriginal || size === 0) {
            this.#api.altTabSmallIconSetDefaultSize();
        } else {
            this.#api.altTabSmallIconSetSize(size);
        }
    }

    /**
     * apply alt tab icon size settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyAltTabIconSize(forceOriginal)
    {
        let size = this.#settings.get_int('alt-tab-icon-size');

        if (forceOriginal || size === 0) {
            this.#api.altTabIconSetDefaultSize();
        } else {
            this.#api.altTabIconSetSize(size);
        }
    }

    /**
     * apply screen sharing indicator settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyScreenSharingIndicator(forceOriginal)
    {
        let status = this.#settings.get_boolean('screen-sharing-indicator');

        if (forceOriginal || status) {
            this.#api.screenSharingIndicatorEnable();
        } else {
            this.#api.screenSharingIndicatorDisable();
        }
    }

    /**
     * apply screen recording indicator settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyScreenRecordingIndicator(forceOriginal)
    {
        let status = this.#settings.get_boolean('screen-recording-indicator');

        if (forceOriginal || status) {
            this.#api.screenRecordingIndicatorEnable();
        } else {
            this.#api.screenRecordingIndicatorDisable();
        }
    }

    /**
     * apply controls manager spacing size settings
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyControlsManagerSpacingSize(forceOriginal)
    {
        let size = this.#settings.get_int('controls-manager-spacing-size');

        if (forceOriginal || size === 0) {
            this.#api.controlsManagerSpacingSetDefault();
        } else {
            this.#api.controlsManagerSpacingSizeSet(size);
        }
    }

    /**
     * apply workspace peek
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyWorkspacePeek(forceOriginal)
    {
        if (forceOriginal || this.#settings.get_boolean('workspace-peek')) {
            this.#api.workspacesViewSpacingSetDefault();
        } else {
            this.#api.workspacesViewSpacingSizeSet(400);
        }
    }
    
    /**
     * apply dash app running
     *
     * @param {boolean} forceOriginal force original shell setting
     *
     * @returns {void}
     */
    #applyDashAppRunning(forceOriginal)
    {
        if (forceOriginal || this.#settings.get_boolean('dash-app-running')) {
            this.#api.dashAppRunningDotShow();
        } else {
            this.#api.dashAppRunningDotHide();
        }
    }
}


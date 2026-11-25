"""PostHog on the pages, in nominal.io's PostHog project, so a visitor who comes from nominal.io stays one person.

LOADER is PostHog's HTML snippet (https://posthog.com/docs/libraries/js), unchanged: it queues calls until the SDK
loads from api_host. A click on a link into the Nominal app is sent as outbound_link_clicked, with the properties
nominal.io sends for it, so one chart covers both sites. The docs hub adds the same script to pages built
without it, from script().
"""

import json

# nominal.io's PostHog project token
TOKEN = "phc_q2ywmahEgRaQgwFoESazhovkXBqW2XuZy5PduwJcMqLD"

# nominal.io's proxy, which forwards to PostHog's US cloud
API_HOST = "https://u2.nominal.io"
UI_HOST = "https://us.posthog.com"
DEFAULTS = "2026-08-30"

LOADER = '!function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],Object.defineProperty(u,"toString",{configurable:!0,enumerable:!0,writable:!0,value:function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e}}),Object.defineProperty(u.people,"toString",{configurable:!0,enumerable:!0,writable:!0,value:function(){return u.toString(1)+".people (stub)"}}),o="init capture register register_once register_for_session unregister unregister_for_session getFeatureFlag getFeatureFlagResult isFeatureEnabled reloadFeatureFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey getNextSurveyStep identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset get_distinct_id getGroups get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording sessionRecordingStarted captureException loadToolbar get_property getSessionProperty createPersonProfile opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing clear_opt_in_out_capturing debug".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);'

# a local preview, or a copy opened from disk, reports nothing
PUBLISHED = r'location.protocol !== "file:" && !/^(localhost|127\.0\.0\.1|\[::1\])$/.test(location.hostname)'

APP_LINK_CLICKS = r"""// a middle click, which opens the link in a new tab, arrives as auxclick
for (const type of ["click", "auxclick"]) document.addEventListener(type, (e) => {
  if (e.type === "auxclick" && e.button !== 1) return;
  const a = e.target instanceof Element && e.target.closest("a[href]");
  if (!a || !/^app\.([\w-]+\.)*nominal\.io$/.test(a.hostname)) return;
  const region = a.closest("header, .sy-head") ? "header" : a.closest("footer") ? "footer" : a.closest("main") ? "main" : "other";
  posthog.capture(
    "outbound_link_clicked",
    { destination: "app", url: a.href, link_text: a.textContent.trim(), page_path: location.pathname, region },
    { transport: "sendBeacon", send_instantly: true },
  );
}, true);"""


def script(token: str) -> str:
    """The script for a page: load PostHog with the project token, and report clicks into the app."""
    config = {"api_host": API_HOST, "ui_host": UI_HOST, "defaults": DEFAULTS}
    return f"if ({PUBLISHED}) {{\n{LOADER}\nposthog.init({json.dumps(token)}, {json.dumps(config)});\n{APP_LINK_CLICKS}\n}}"

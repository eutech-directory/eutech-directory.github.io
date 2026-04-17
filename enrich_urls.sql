-- enrich_urls.sql
-- Run with: psql postgresql://agentuser:agentstack123@localhost:5432/agentstack -f enrich_urls.sql

UPDATE eu_alternatives SET website = 'https://plausible.io' WHERE LOWER(name) = 'plausible' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://simpleanalytics.com' WHERE LOWER(name) = 'simple analytics' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://piwik.pro' WHERE LOWER(name) = 'piwik pro' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://visitoranalytics.io' WHERE LOWER(name) = 'visitor analytics' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://pirsch.io' WHERE LOWER(name) = 'pirsch' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://etracker.com' WHERE LOWER(name) = 'etracker' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://wideangle.co' WHERE LOWER(name) = 'wide angle analytics' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://telemetrydeck.com' WHERE LOWER(name) = 'telemetrydeck' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://mouseflow.com' WHERE LOWER(name) = 'mouseflow' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://matomo.org' WHERE LOWER(name) = 'matomo' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://contentsquare.com' WHERE LOWER(name) = 'contentsquare' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://hotjar.com' WHERE LOWER(name) = 'hotjar' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://hetzner.com' WHERE LOWER(name) = 'hetzner' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://ovhcloud.com' WHERE LOWER(name) = 'ovhcloud' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://scaleway.com' WHERE LOWER(name) = 'scaleway' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://exoscale.com' WHERE LOWER(name) = 'exoscale' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://infomaniak.com' WHERE LOWER(name) LIKE '%infomaniak%' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://bunny.net' WHERE LOWER(name) LIKE '%bunny%' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://ionos.com' WHERE LOWER(name) = 'ionos' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://netcup.eu' WHERE LOWER(name) = 'netcup' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://protonmail.com' WHERE LOWER(name) = 'proton mail' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://proton.me' WHERE LOWER(name) = 'proton' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://tutanota.com' WHERE LOWER(name) = 'tutanota' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://mailfence.com' WHERE LOWER(name) = 'mailfence' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://posteo.de' WHERE LOWER(name) = 'posteo' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://fastmail.com' WHERE LOWER(name) = 'fastmail' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://nextcloud.com' WHERE LOWER(name) = 'nextcloud' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://tresorit.com' WHERE LOWER(name) = 'tresorit' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://pcloud.com' WHERE LOWER(name) = 'pcloud' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://jottacloud.com' WHERE LOWER(name) = 'jottacloud' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://gitlab.com' WHERE LOWER(name) = 'gitlab' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://gitea.io' WHERE LOWER(name) = 'gitea' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://forgejo.org' WHERE LOWER(name) = 'forgejo' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://codeberg.org' WHERE LOWER(name) = 'codeberg' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://bitwarden.com' WHERE LOWER(name) = 'bitwarden' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://vaultwarden.net' WHERE LOWER(name) = 'vaultwarden' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://keepassxc.org' WHERE LOWER(name) = 'keepassxc' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://psono.com' WHERE LOWER(name) = 'psono' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://n26.com' WHERE LOWER(name) = 'n26' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://bunq.com' WHERE LOWER(name) = 'bunq' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://revolut.com' WHERE LOWER(name) = 'revolut' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://sumup.com' WHERE LOWER(name) = 'sumup' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://mollie.com' WHERE LOWER(name) = 'mollie' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://adyen.com' WHERE LOWER(name) = 'adyen' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://homeassistant.io' WHERE LOWER(name) = 'home assistant' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://openhab.org' WHERE LOWER(name) = 'openhab' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://shelly.cloud' WHERE LOWER(name) LIKE '%shelly%' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://netatmo.com' WHERE LOWER(name) = 'netatmo' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://nuki.io' WHERE LOWER(name) = 'nuki' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://tado.com' WHERE LOWER(name) LIKE '%tado%' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://sketch.com' WHERE LOWER(name) = 'sketch' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://anytype.io' WHERE LOWER(name) = 'anytype' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://shopware.com' WHERE LOWER(name) = 'shopware' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://malt.com' WHERE LOWER(name) = 'malt' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://jimdo.com' WHERE LOWER(name) = 'jimdo' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://tomtom.com' WHERE LOWER(name) = 'tomtom' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://waze.com' WHERE LOWER(name) = 'here wego' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://here.com' WHERE LOWER(name) = 'here wego' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://bitdefender.com' WHERE LOWER(name) = 'bitdefender' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://eset.com' WHERE LOWER(name) = 'eset' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://kaspersky.com' WHERE LOWER(name) = 'kaspersky' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://abfahrt.app' WHERE LOWER(name) LIKE '%abfahrt%' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://lavera.de' WHERE LOWER(name) = 'lavera' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://yves-rocher.com' WHERE LOWER(name) = 'yves rocher' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://loreal.com' WHERE LOWER(name) LIKE '%l%oreal%' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://kikocosmetics.com' WHERE LOWER(name) LIKE '%kiko%' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://catrice.eu' WHERE LOWER(name) = 'catrice' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://open-xchange.com' WHERE LOWER(name) LIKE '%open.xchange%' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://cryptpad.fr' WHERE LOWER(name) = 'cryptpad' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://jitsi.org' WHERE LOWER(name) = 'jitsi' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://element.io' WHERE LOWER(name) = 'element' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://matrix.org' WHERE LOWER(name) = 'matrix' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://signal.org' WHERE LOWER(name) = 'signal' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://wire.com' WHERE LOWER(name) = 'wire' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://threema.ch' WHERE LOWER(name) = 'threema' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://xwiki.com' WHERE LOWER(name) = 'xwiki' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://openproject.org' WHERE LOWER(name) = 'openproject' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://taiga.io' WHERE LOWER(name) = 'taiga' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://wekan.github.io' WHERE LOWER(name) = 'wekan' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://framasoft.org' WHERE LOWER(name) = 'framasoft' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://peertube.tv' WHERE LOWER(name) = 'peertube' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://mastodon.social' WHERE LOWER(name) = 'mastodon' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://pixelfed.org' WHERE LOWER(name) = 'pixelfed' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://searxng.org' WHERE LOWER(name) LIKE '%searx%' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://startpage.com' WHERE LOWER(name) = 'startpage' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://qwant.com' WHERE LOWER(name) = 'qwant' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://ecosia.org' WHERE LOWER(name) = 'ecosia' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://swisscom.ch' WHERE LOWER(name) = 'swisscom' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://deutsche-telekom.com' WHERE LOWER(name) LIKE '%telekom%' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://kimsufi.com' WHERE LOWER(name) = 'kimsufi' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://contabo.com' WHERE LOWER(name) = 'contabo' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://strato.de' WHERE LOWER(name) = 'strato' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://mittwald.de' WHERE LOWER(name) = 'mittwald' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://hosteurope.de' WHERE LOWER(name) LIKE '%host europe%' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://upcloud.com' WHERE LOWER(name) = 'upcloud' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://citynetwork.eu' WHERE LOWER(name) LIKE '%city network%' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://cleura.com' WHERE LOWER(name) = 'cleura' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://elastx.se' WHERE LOWER(name) = 'elastx' AND (website IS NULL OR website = '');
UPDATE eu_alternatives SET website = 'https://safespring.com' WHERE LOWER(name) = 'safespring' AND (website IS NULL OR website = '');

-- Update category counts
UPDATE eu_categories ec
SET tool_count = sub.cnt
FROM (
    SELECT category, COUNT(*) AS cnt
    FROM eu_alternatives
    GROUP BY category
) sub
WHERE ec.name = sub.category;

SELECT COUNT(*) as tools_with_urls FROM eu_alternatives WHERE website IS NOT NULL AND website != '';
SELECT COUNT(*) as total_tools FROM eu_alternatives;

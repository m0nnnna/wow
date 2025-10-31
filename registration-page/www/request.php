<?php
// Include the characters DB connection
include 'C:\laragon\db_connect_chars.php'; // Adjust path if needed; assumes it sets $pdo_chars

// Define the rewards with categories
$rewards = [    1 => [
        'category' => 'Daily Rewards',
        'name' => 'Daily Gift',
        'reset_time' => '05:00:00',
        'timezone' => 'America/New_York',
        'type' => 'daily_gift'
    ],
    2 => [
        'category' => 'Level Rewards',
        'name' => 'Level 40 Gold Reward',
        'req_level' => 40,
        'reward_gold' => 1000000,
        'type' => 'one_time_level'
    ],
    4 => [
        'boss_name' => 'Ragnaros',
        'category' => 'Raid Rewards',
        'criteria_id' => 3665,
        'name' => 'Bindings of The WindSeeker Right',
        'req_kills' => 50,
        'reward_item_id' => 18564,
        'type' => 'boss_kill'
    ],
    5 => [
        'boss_name' => 'Ragnaros',
        'category' => 'Raid Rewards',
        'criteria_id' => 3665,
        'name' => 'Bindings of The WindSeeker Left',
        'req_kills' => 100,
        'reward_item_id' => 18564,
        'type' => 'boss_kill'
    ],
    6 => [
        'boss_name' => 'Emperor Dagran Thaurissan',
        'category' => 'Rogue Rewards',
        'criteria_id' => 9019,
        'name' => 'Shadowcraft Cap',
        'req_kills' => 25,
        'reward_item_id' => 16707,
        'type' => 'boss_kill'
    ],
    7 => [
        'boss_name' => 'Baron Rivendare',
        'category' => 'Rogue Rewards',
        'criteria_id' => 10440,
        'name' => 'Shadowcraft Pants',
        'req_kills' => 25,
        'reward_item_id' => 16709,
        'type' => 'boss_kill'
    ],
    8 => [
        'boss_name' => 'General Drakkisath',
        'category' => 'Rogue Rewards',
        'criteria_id' => 10363,
        'name' => 'Shadowcraft Tunic',
        'req_kills' => 25,
        'reward_item_id' => 16721,
        'type' => 'boss_kill'
    ],
    9 => [
        'boss_name' => 'Baron Rivendare',
        'category' => 'Rogue Rewards',
        'criteria_id' => 10440,
        'name' => 'Shadowcraft Gloves',
        'req_kills' => 50,
        'reward_item_id' => 16712,
        'type' => 'boss_kill'
    ],
    10 => [
        'boss_name' => 'General Drakkisath',
        'category' => 'Rogue Rewards',
        'criteria_id' => 10363,
        'name' => 'Shadowcraft Bracers',
        'req_kills' => 50,
        'reward_item_id' => 16710,
        'type' => 'boss_kill'
    ],
    11 => [
        'boss_name' => 'Emperor Dagran Thaurissan',
        'category' => 'Rogue Rewards',
        'criteria_id' => 9019,
        'name' => 'Shadowcraft Boots',
        'req_kills' => 50,
        'reward_item_id' => 16711,
        'type' => 'boss_kill'
    ],
    12 => [
        'boss_name' => 'Scarlet Commander Mograine',
        'category' => 'Rogue Rewards',
        'criteria_id' => 3976,
        'name' => 'Shadowcraft Belt',
        'req_kills' => 25,
        'reward_item_id' => 16713,
        'type' => 'boss_kill'
    ],
    13 => [
        'boss_name' => 'Edwin VanCleef',
        'category' => 'Rogue Rewards',
        'criteria_id' => 3262,
        'name' => 'Shadowcraft Spaulders',
        'req_kills' => 25,
        'reward_item_id' => 16708,
        'type' => 'boss_kill'
    ],
    14 => [
        'boss_name' => 'Emperor Dagran Thaurissan',
        'category' => 'Druid Rewards',
        'criteria_id' => 542,
        'name' => 'Wildheart Belt',
        'req_kills' => 25,
        'reward_item_id' => 16716,
        'stack_size' => 1,
        'type' => 'boss_kill'
    ],
    15 => [
        'boss_name' => 'Baron Rivendare',
        'category' => 'Druid Rewards',
        'criteria_id' => 551,
        'name' => 'Wildheart Boots',
        'req_kills' => 25,
        'reward_item_id' => 16715,
        'stack_size' => 1,
        'type' => 'boss_kill'
    ],
    16 => [
        'boss_name' => 'General Drakkisath',
        'category' => 'Druid Rewards',
        'criteria_id' => 3268,
        'name' => 'Wildheart Bracers',
        'req_kills' => 25,
        'reward_item_id' => 16714,
        'stack_size' => 1,
        'type' => 'boss_kill'
    ],
    17 => [
        'boss_name' => 'Scarlet Commander Mograine',
        'category' => 'Druid Rewards',
        'criteria_id' => 534,
        'name' => 'Wildheart Cowl',
        'req_kills' => 25,
        'reward_item_id' => 16720,
        'stack_size' => 1,
        'type' => 'boss_kill'
    ],
    18 => [
        'boss_name' => 'Edwin VanCleef',
        'category' => 'Druid Rewards',
        'criteria_id' => 3262,
        'name' => 'Wildheart Gloves',
        'req_kills' => 25,
        'reward_item_id' => 16717,
        'stack_size' => 1,
        'type' => 'boss_kill'
    ],
    19 => [
        'boss_name' => 'General Drakkisath',
        'category' => 'Druid Rewards',
        'criteria_id' => 3268,
        'name' => 'Wildheart Kilt',
        'req_kills' => 50,
        'reward_item_id' => 16719,
        'stack_size' => 1,
        'type' => 'boss_kill'
    ],
    20 => [
        'boss_name' => 'Baron Rivendare',
        'category' => 'Druid Rewards',
        'criteria_id' => 551,
        'name' => 'Wildheart Spaulders',
        'req_kills' => 50,
        'reward_item_id' => 16718,
        'stack_size' => 1,
        'type' => 'boss_kill'
    ],
    21 => [
        'boss_name' => 'Emperor Dagran Thaurissan',
        'category' => 'Druid Rewards',
        'criteria_id' => 542,
        'name' => 'Wildheart Vest',
        'req_kills' => 50,
        'reward_item_id' => 16706,
        'stack_size' => 1,
        'type' => 'boss_kill'
    ]];

// Define level-tiered items for daily gift (health pot, mana pot, food)
// Extended health potions (restores health; standard progression)
$health_pots = [    1 => 118,
    3 => 858,
    12 => 929,
    21 => 1710,
    31 => 3928,
    41 => 13446,
    51 => 18253,
    65 => 22850,
    71 => 33447];

// Extended mana potions (restores mana; standard progression)
$mana_pots = [    5 => 2455,
    14 => 3385,
    22 => 3827,
    31 => 6149,
    41 => 13443,
    49 => 13444,
    51 => 42545,
    65 => 22850,
    71 => 33448];

// Extended foods (basic well-fed buffs; +HP only, no special stats; progression via cooking/vendor)
$foods = [    1 => 117,
    5 => 2287,
    15 => 3770,
    25 => 3771,
    35 => 4599,
    45 => 12224,
    55 => 27661,
    65 => 35949,
	70 => 34747,
    75 => 45932,
    80 => 43523];

// Function to get item ID for level (highest <= char_level)
function get_item_for_level($level, $items_dict) {
    krsort($items_dict); // Sort keys descending
    foreach ($items_dict as $req_level => $item_id) {
        if ($level >= $req_level) {
            return $item_id;
        }
    }
    return end($items_dict); // Lowest if none match
}

// Cooldown in seconds for boss_kill types (2 hours = 7200 seconds)
$cooldown_seconds = 7200;

$errors = [];
$success = false;
$char_level = 0;
$char_kills = 0;

// Ensure PDO connection is available
if (!isset($pdo_chars)) {
    $errors[] = 'Database connection not available.';
}

// Check/create rewards_log table
try {
    $pdo_chars->query("SELECT 1 FROM rewards_log LIMIT 1");
} catch (PDOException $e) {
    if (strpos($e->getMessage(), 'no such table') !== false || strpos($e->getMessage(), 'doesn\'t exist') !== false) {
        $pdo_chars->exec("
            CREATE TABLE IF NOT EXISTS rewards_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                guid INT NOT NULL,
                reward_key INT NOT NULL,
                item_id INT DEFAULT NULL,
                gold INT DEFAULT NULL,
                stack_size INT DEFAULT NULL,
                request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ");
    } else {
        $errors[] = 'Table check failed: ' . htmlspecialchars($e->getMessage());
    }
}

if (empty($errors) && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $char_name = trim($_POST['char_name'] ?? '');
    $reward_selected = intval($_POST['reward_key'] ?? 0);

    // Basic validation
    if (empty($char_name) || strlen($char_name) < 2 || strlen($char_name) > 12 || !preg_match('/^[a-zA-Z0-9]+$/', $char_name)) {
        $errors[] = 'Character name must be 2-12 alphanumeric characters.';
    }
    if (!array_key_exists($reward_selected, $rewards)) {
        $errors[] = 'Invalid reward selected.';
    }

    if (empty($errors)) {
        try {
            // Find character GUID and level
            $stmt = $pdo_chars->prepare("SELECT guid, level FROM characters WHERE name = :name");
            $stmt->execute(['name' => $char_name]);
            $char = $stmt->fetch(PDO::FETCH_ASSOC);
            
            if (!$char) {
                throw new Exception('Character not found. Ensure the name is exact (case-sensitive).');
            }
            $guid = $char['guid'];
            $char_level = (int)$char['level'];

            $reward = $rewards[$reward_selected];
            $reward_type = $reward['type'];
            $reward_name = $reward['name'];
            $item_guids = [];
            $gold = $reward['reward_gold'] ?? 0;
            $body_extras = [];

		if ($reward_type === 'boss_kill') {
			// Cooldown check
			$stmt_cd = $pdo_chars->prepare("SELECT MAX(request_time) AS last_request FROM rewards_log WHERE guid = :guid AND reward_key IN (SELECT array_to_string(ARRAY(SELECT key FROM rewards WHERE type = 'boss_kill'), ','))");
			$stmt_cd->execute(['guid' => $guid]);
			$last_req = $stmt_cd->fetch(PDO::FETCH_ASSOC)['last_request'];

			if ($last_req) {
				$last_time = strtotime($last_req);
				$current_time = time();
				if ($current_time - $last_time < $cooldown_seconds) {
					$remaining = $cooldown_seconds - ($current_time - $last_time);
					$hours = floor($remaining / 3600);
					$mins = floor(($remaining % 3600) / 60);
					$secs = $remaining % 60;
					throw new Exception("You must wait {$hours}h {$mins}m {$secs}s before requesting another boss reward.");
				}
			}

			// Support both single boss (criteria_id) and multiple bosses (criteria_ids)
			if (isset($reward['criteria_ids']) && is_array($reward['criteria_ids'])) {
				// Multiple bosses - check if any boss meets requirement
				$criteria_ids = $reward['criteria_ids'];
				$boss_names = $reward['boss_names'] ?? $criteria_ids; // fallback if no boss_names
				$req_kills = $reward['req_kills'];
				$char_kills = 0;
				$qualified_boss = '';
				$met_requirement = false;

				foreach ($criteria_ids as $index => $criteria_id) {
					$stmt = $pdo_chars->prepare("SELECT counter FROM character_achievement_progress WHERE guid = :guid AND criteria = :criteria");
					$stmt->execute(['guid' => $guid, 'criteria' => $criteria_id]);
					$progress = $stmt->fetch(PDO::FETCH_ASSOC);
					$kills = $progress ? (int)$progress['counter'] : 0;
					
					if ($kills >= $req_kills) {
						$met_requirement = true;
						$char_kills = $kills;
						$qualified_boss = isset($boss_names[$index]) ? $boss_names[$index] : "Boss $criteria_id";
						break;
					}
				}

				if (!$met_requirement) {
					$boss_list = [];
					foreach ($criteria_ids as $index => $criteria_id) {
						$boss_name = isset($boss_names[$index]) ? $boss_names[$index] : "Boss $criteria_id";
						$boss_list[] = "$boss_name ($req_kills kills)";
					}
					$boss_list_str = implode(' or ', $boss_list);
					throw new Exception("You need at least $req_kills kills of $boss_list_str to request '$reward_name'.");
				}
			} else {
				// Single boss (backward compatibility)
				$criteria_id = $reward['criteria_id'];
				$stmt = $pdo_chars->prepare("SELECT counter FROM character_achievement_progress WHERE guid = :guid AND criteria = :criteria");
				$stmt->execute(['guid' => $guid, 'criteria' => $criteria_id]);
				$progress = $stmt->fetch(PDO::FETCH_ASSOC);
				$char_kills = $progress ? (int)$progress['counter'] : 0;

				$req_kills = $reward['req_kills'];
				$boss_name = $reward['boss_name'];
				if ($char_kills < $req_kills) {
					throw new Exception("You need at least $req_kills $boss_name kills to request '$reward_name'. You have $char_kills.");
				}
				$qualified_boss = $boss_name;
			}

			$item_id = $reward['reward_item_id'] ?? 0;
			$stack_size = $reward['stack_size'] ?? 1;
			if ($item_id > 0) {
                    $stmt_item_info = $pdo_chars->prepare("SELECT maxDurability, stackable, name, spellcharges_1, spellcharges_2, spellcharges_3, spellcharges_4, spellcharges_5 FROM acore_world.item_template WHERE entry = :entry");
                    $stmt_item_info->execute(['entry' => $item_id]);
                    $item_info = $stmt_item_info->fetch(PDO::FETCH_ASSOC);
                    if (!$item_info) {
                        throw new Exception("Invalid item ID $item_id for '$reward_name'.");
                    }
                    $max_dura = (int)$item_info['maxDurability'];
                    $max_stack = (int)$item_info['stackable'];
                    if ($stack_size > $max_stack) {
                        throw new Exception("Stack size $stack_size exceeds max stack of $max_stack for '$reward_name'.");
                    }
                    $item_name = $item_info['name'];

                    $enchantments = implode(' ', array_fill(0, 36, 0));
                    $charges = $item_info['spellcharges_1'] . ' ' . $item_info['spellcharges_2'] . ' ' . $item_info['spellcharges_3'] . ' ' . $item_info['spellcharges_4'] . ' ' . $item_info['spellcharges_5'];

                    try {
                        $pdo_chars->exec("ALTER TABLE item_instance MODIFY COLUMN guid INT UNSIGNED NOT NULL AUTO_INCREMENT");
                    } catch (PDOException $alter_e) {
                        // Ignore if already set
                    }

                    $stmt_item = $pdo_chars->prepare("
                        INSERT INTO item_instance 
                        (itemEntry, owner_guid, count, duration, charges, flags, enchantments, randomPropertyId, durability, playedTime, text) 
                        VALUES (:itemEntry, 0, :count, 0, :charges, 0, :enchantments, 0, :durability, 0, '')
                    ");
                    $stmt_item->execute([
                        'itemEntry' => $item_id,
                        'count' => $stack_size,
                        'charges' => $charges,
                        'enchantments' => $enchantments,
                        'durability' => $max_dura
                    ]);
                    if ($stmt_item->rowCount() !== 1) {
                        throw new Exception("Failed to create item instance for '$reward_name'.");
                    }
                    $item_guid = $pdo_chars->lastInsertId();
                    if ($item_guid <= 0) {
                        $max_guid = $pdo_chars->query("SELECT COALESCE(MAX(guid), 0) FROM item_instance")->fetchColumn();
                        $pdo_chars->exec("ALTER TABLE item_instance AUTO_INCREMENT = " . ($max_guid + 1));
                        $stmt_item->execute([
                            'itemEntry' => $item_id,
                            'count' => $stack_size,
                            'charges' => $charges,
                            'enchantments' => $enchantments,
                            'durability' => $max_dura
                        ]);
                        $item_guid = $pdo_chars->lastInsertId();
                        if ($item_guid <= 0) {
                            throw new Exception("Invalid item GUID for '$reward_name'. Contact admin to fix item_instance AUTO_INCREMENT.");
                        }
                    }
                    $item_guids[] = $item_guid;
                    $body_extras[] = "$item_name x$stack_size";
                    error_log("Item created: GUID=$item_guid, ItemID=$item_id, Reward='$reward_name' for GUID=$guid");
                }
            } elseif ($reward_type === 'one_time_level') {
                $req_level = $reward['req_level'];
                if ($char_level < $req_level) {
                    throw new Exception("You need to be at least level $req_level to claim '$reward_name'. You are level $char_level.");
                }

                $stmt_check = $pdo_chars->prepare("SELECT COUNT(*) FROM rewards_log WHERE guid = :guid AND reward_key = :reward_key");
                $stmt_check->execute(['guid' => $guid, 'reward_key' => $reward_selected]);
                if ($stmt_check->fetchColumn() > 0) {
                    throw new Exception("You have already claimed the one-time reward '$reward_name'.");
                }

                // Handle single or multiple items
                $item_ids = $reward['reward_item_ids'] ?? [$reward['reward_item_id'] ?? 0];
                $stack_sizes = $reward['stack_sizes'] ?? [$reward['stack_size'] ?? 1];
                if (count($item_ids) !== count($stack_sizes)) {
                    throw new Exception("Mismatch between item IDs and stack sizes for '$reward_name'.");
                }

                foreach (array_combine($item_ids, $stack_sizes) as $item_id => $stack_size) {
                    if ($item_id > 0) {
                        $stmt_item_info = $pdo_chars->prepare("SELECT maxDurability, stackable, name, spellcharges_1, spellcharges_2, spellcharges_3, spellcharges_4, spellcharges_5 FROM acore_world.item_template WHERE entry = :entry");
                        $stmt_item_info->execute(['entry' => $item_id]);
                        $item_info = $stmt_item_info->fetch(PDO::FETCH_ASSOC);
                        if (!$item_info) {
                            throw new Exception("Invalid item ID $item_id for '$reward_name'.");
                        }
                        $max_dura = (int)$item_info['maxDurability'];
                        $max_stack = (int)$item_info['stackable'];
                        if ($stack_size > $max_stack) {
                            throw new Exception("Stack size $stack_size exceeds max stack of $max_stack for item ID $item_id in '$reward_name'.");
                        }
                        $item_name = $item_info['name'];

                        $enchantments = implode(' ', array_fill(0, 36, 0));
                        $charges = $item_info['spellcharges_1'] . ' ' . $item_info['spellcharges_2'] . ' ' . $item_info['spellcharges_3'] . ' ' . $item_info['spellcharges_4'] . ' ' . $item_info['spellcharges_5'];

                        $stmt_item = $pdo_chars->prepare("
                            INSERT INTO item_instance 
                            (itemEntry, owner_guid, count, duration, charges, flags, enchantments, randomPropertyId, durability, playedTime, text) 
                            VALUES (:itemEntry, 0, :count, 0, :charges, 0, :enchantments, 0, :durability, 0, '')
                        ");
                        $stmt_item->execute([
                            'itemEntry' => $item_id,
                            'count' => $stack_size,
                            'charges' => $charges,
                            'enchantments' => $enchantments,
                            'durability' => $max_dura
                        ]);
                        if ($stmt_item->rowCount() !== 1) {
                            throw new Exception("Failed to create item instance for item ID $item_id in '$reward_name'.");
                        }
                        $item_guid = $pdo_chars->lastInsertId();
                        if ($item_guid <= 0) {
                            $max_guid = $pdo_chars->query("SELECT COALESCE(MAX(guid), 0) FROM item_instance")->fetchColumn();
                            $pdo_chars->exec("ALTER TABLE item_instance AUTO_INCREMENT = " . ($max_guid + 1));
                            $stmt_item->execute([
                                'itemEntry' => $item_id,
                                'count' => $stack_size,
                                'charges' => $charges,
                                'enchantments' => $enchantments,
                                'durability' => $max_dura
                            ]);
                            $item_guid = $pdo_chars->lastInsertId();
                            if ($item_guid <= 0) {
                                throw new Exception("Invalid item GUID for item ID $item_id in '$reward_name'. Contact admin to fix item_instance AUTO_INCREMENT.");
                            }
                        }
                        $item_guids[] = $item_guid;
                        $body_extras[] = "$item_name x$stack_size";
                        error_log("Item created: GUID=$item_guid, ItemID=$item_id, Reward='$reward_name' for GUID=$guid");
                    }
                }
            } elseif ($reward_type === 'daily_gift') {
                $reset_time_str = $reward['reset_time'];
                $timezone = new DateTimeZone($reward['timezone']);
                $now = new DateTime('now', $timezone);
                $today_reset = new DateTime($now->format('Y-m-d') . ' ' . $reset_time_str, $timezone);

                if ($now < $today_reset) {
                    $today_reset->modify('-1 day');
                }

                $stmt_cd = $pdo_chars->prepare("SELECT MAX(request_time) AS last_claim FROM rewards_log WHERE guid = :guid AND reward_key = :reward_key");
                $stmt_cd->execute(['guid' => $guid, 'reward_key' => $reward_selected]);
                $last_claim_str = $stmt_cd->fetch(PDO::FETCH_ASSOC)['last_claim'];
                $last_claim = $last_claim_str ? new DateTime($last_claim_str, new DateTimeZone('UTC')) : null;
                if ($last_claim) {
                    $last_claim->setTimezone($timezone);
                }

                if ($last_claim && $last_claim >= $today_reset) {
                    $next_reset = clone $today_reset;
                    $next_reset->modify('+1 day');
                    $remaining = $next_reset->diff($now);
                    throw new Exception("You have already claimed the daily gift today. Next available in " . $remaining->format('%h hours %i minutes %s seconds') . ".");
                }

                $gift_items = [
                    'Health Potion' => get_item_for_level($char_level, $health_pots),
                    'Mana Potion' => get_item_for_level($char_level, $mana_pots),
                    'Food' => get_item_for_level($char_level, $foods)
                ];
                $stack_size = 20;

                foreach ($gift_items as $type => $item_id) {
                    $stmt_item_info = $pdo_chars->prepare("SELECT maxDurability, stackable, name, spellcharges_1, spellcharges_2, spellcharges_3, spellcharges_4, spellcharges_5 FROM acore_world.item_template WHERE entry = :entry");
                    $stmt_item_info->execute(['entry' => $item_id]);
                    $item_info = $stmt_item_info->fetch(PDO::FETCH_ASSOC);
                    if (!$item_info) {
                        throw new Exception("Invalid item ID $item_id for daily $type.");
                    }
                    $max_dura = (int)$item_info['maxDurability'];
                    $max_stack = (int)$item_info['stackable'];
                    if ($stack_size > $max_stack) {
                        throw new Exception("Stack size $stack_size exceeds max stack of $max_stack for daily $type.");
                    }
                    $item_name = $item_info['name'];

                    $enchantments = implode(' ', array_fill(0, 36, 0));
                    $charges = $item_info['spellcharges_1'] . ' ' . $item_info['spellcharges_2'] . ' ' . $item_info['spellcharges_3'] . ' ' . $item_info['spellcharges_4'] . ' ' . $item_info['spellcharges_5'];

                    $stmt_item = $pdo_chars->prepare("
                        INSERT INTO item_instance 
                        (itemEntry, owner_guid, count, duration, charges, flags, enchantments, randomPropertyId, durability, playedTime, text) 
                        VALUES (:itemEntry, 0, :count, 0, :charges, 0, :enchantments, 0, :durability, 0, '')
                    ");
                    $stmt_item->execute([
                        'itemEntry' => $item_id,
                        'count' => $stack_size,
                        'charges' => $charges,
                        'enchantments' => $enchantments,
                        'durability' => $max_dura
                    ]);
                    if ($stmt_item->rowCount() !== 1) {
                        throw new Exception("Failed to create item instance for daily $type.");
                    }
                    $item_guid = $pdo_chars->lastInsertId();
                    if ($item_guid <= 0) {
                        $max_guid = $pdo_chars->query("SELECT COALESCE(MAX(guid), 0) FROM item_instance")->fetchColumn();
                        $pdo_chars->exec("ALTER TABLE item_instance AUTO_INCREMENT = " . ($max_guid + 1));
                        $stmt_item->execute([
                            'itemEntry' => $item_id,
                            'count' => $stack_size,
                            'charges' => $charges,
                            'enchantments' => $enchantments,
                            'durability' => $max_dura
                        ]);
                        $item_guid = $pdo_chars->lastInsertId();
                        if ($item_guid <= 0) {
                            throw new Exception("Invalid item GUID for daily $type. Contact admin to fix item_instance AUTO_INCREMENT.");
                        }
                    }
                    $item_guids[] = $item_guid;
                    $body_extras[] = "$item_name x$stack_size";
                    error_log("Daily item created: GUID=$item_guid, ItemID=$item_id, Type=$type for GUID=$guid");
                }
            } else {
                throw new Exception('Unknown reward type.');
            }

			// Create mail
			$current_time = time();
			$deliver_time = $current_time;
			$expire_time = $current_time + (30 * 24 * 3600);
			$subject = "Reward: $reward_name";
			$body = "Congratulations! You've claimed the $reward_name.";
			if ($reward_type === 'boss_kill' && isset($qualified_boss)) {
				$body .= " (Earned via $qualified_boss kills)";
			}
			if (!empty($body_extras)) {
				$body .= " Including: " . implode(', ', $body_extras);
			} elseif ($gold > 0) {
				$body .= " (" . ($gold / 10000) . " gold)";
			}

            $stmt_mail = $pdo_chars->prepare("
                INSERT INTO mail 
                (messageType, stationery, mailTemplateId, sender, receiver, subject, body, has_items, expire_time, deliver_time, money, cod, checked) 
                VALUES (0, 41, 0, 0, :receiver, :subject, :body, :has_items, :expire_time, :deliver_time, :money, 0, 0)
            ");
            $stmt_mail->execute([
                'receiver' => $guid,
                'subject' => $subject,
                'body' => $body,
                'has_items' => (!empty($item_guids) ? 1 : 0),
                'expire_time' => $expire_time,
                'deliver_time' => $deliver_time,
                'money' => $gold
            ]);
            if ($stmt_mail->rowCount() !== 1) {
                throw new Exception('Failed to create mail entry.');
            }
            $mail_id = $pdo_chars->lastInsertId();
            if ($mail_id <= 0) {
                throw new Exception('Invalid mail ID generated.');
            }

            foreach ($item_guids as $item_guid) {
                $stmt_attach = $pdo_chars->prepare("INSERT INTO mail_items (mail_id, item_guid, receiver) VALUES (:mail_id, :item_guid, :receiver)");
                $stmt_attach->execute([
                    'mail_id' => $mail_id,
                    'item_guid' => $item_guid,
                    'receiver' => $guid
                ]);
                if ($stmt_attach->rowCount() !== 1) {
                    throw new Exception('Failed to attach item to mail.');
                }
            }

            // Log the claim (log first item_id for non-daily, null for daily)
            $stmt_log = $pdo_chars->prepare("INSERT INTO rewards_log (guid, reward_key, item_id, gold, stack_size) VALUES (:guid, :reward_key, :item_id, :gold, :stack_size)");
			$stmt_log->execute([
				'guid' => $guid,
				'reward_key' => $reward_selected,
				'item_id' => $reward_type === 'daily_gift' ? null : (isset($item_ids[0]) ? $item_ids[0] : ($reward['reward_item_id'] ?? null)),
				'gold' => $gold ?: null,
				'stack_size' => $reward_type === 'daily_gift' ? 20 : (isset($stack_sizes[0]) ? $stack_sizes[0] : ($reward['stack_size'] ?? null))
			]);
            if ($stmt_log->rowCount() !== 1) {
                throw new Exception('Failed to log reward claim.');
            }

            error_log("Mail sent: ID=$mail_id, Items=" . count($item_guids) . ", Reward='$reward_name' to GUID=$guid");

            $success = true;
            $errors = [];

        } catch (Exception $e) {
            $errors[] = htmlspecialchars($e->getMessage());
        } catch (PDOException $e) {
            if (strpos($e->getMessage(), 'Duplicate entry') !== false) {
                $errors[] = 'Item creation failed due to database issue. Contact admin to run: ALTER TABLE item_instance AUTO_INCREMENT = (SELECT COALESCE(MAX(guid), 0) + 1 FROM item_instance);';
            } else {
                $errors[] = 'Database error: ' . htmlspecialchars($e->getMessage());
            }
        }
    }
}

// Group rewards by category for display
$categories = [];
foreach ($rewards as $key => $reward) {
    $category = $reward['category'] ?? 'Uncategorized';
    if (!isset($categories[$category])) {
        $categories[$category] = [];
    }
    $categories[$category][$key] = $reward;
}

// HTML output
echo '<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NekoCore Reward Request</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 500px; 
            margin: 0 auto; 
            padding: 20px; 
            background-color: #f8f9fa; 
        }
        h2 { color: #333; }
        label { 
            display: block; 
            margin-top: 15px; 
            font-weight: bold; 
        }
        input { 
            display: block; 
            width: 100%; 
            margin-bottom: 10px; 
            padding: 8px; 
            border: 1px solid #ddd; 
            border-radius: 4px; 
            box-sizing: border-box;
        }
        button { 
            padding: 12px; 
            background: #007bff; 
            color: white; 
            border: none; 
            cursor: pointer; 
            border-radius: 4px; 
            width: 100%; 
            font-size: 16px;
        }
        button:hover { background: #0056b3; }
        .error { 
            color: #dc3545; 
            background: #f8d7da; 
            border: 1px solid #f5c6cb; 
            padding: 10px; 
            border-radius: 4px; 
            margin-bottom: 15px;
        }
        .success { 
            color: #155724; 
            background: #d4edda; 
            border: 1px solid #c3e6cb; 
            padding: 10px; 
            border-radius: 4px; 
            margin-bottom: 15px;
        }
        .info { 
            background: #d1ecf1; 
            border: 1px solid #bee5eb; 
            padding: 10px; 
            border-radius: 4px; 
            margin-bottom: 15px; 
            color: #0c5460;
        }
        .nav { 
            margin-top: 20px; 
            text-align: center; 
        }
        .nav a { 
            color: #007bff; 
            text-decoration: none; 
            margin: 0 10px; 
        }
        .nav a:hover { text-decoration: underline; }
        ul { margin: 0; padding-left: 20px; }
        .category-header { 
            background: #007bff; 
            color: white; 
            padding: 10px; 
            margin: 5px 0; 
            cursor: pointer; 
            border-radius: 4px; 
            font-weight: bold;
        }
        .category-header:hover { background: #0056b3; }
        .category-content { 
            border: 1px solid #ddd; 
            border-radius: 4px; 
            padding: 8px; 
            background: white; 
            display: none;
        }
        .category-content.active { display: block; }
        .reward-item { 
            padding: 8px; 
            cursor: pointer; 
            border-bottom: 1px solid #eee; 
        }
        .reward-item:last-child { border-bottom: none; }
        .reward-item:hover { background: #f0f0f0; }
        .reward-item.selected { background: #e7f3ff; }
    </style>
</head>
<body>
    <h2>NekoCore Reward Request</h2>
    
    <div class="info">
        <p>Enter your character name and select a reward by clicking it. Use the search box to filter all rewards (ignores categories). Click category headers to expand/collapse.</p>
        <p>Note: Boss rewards have a 2-hour cooldown; level rewards are one-time; dailies reset at 5am EST.</p>
    </div>';

if (!empty($errors)) {
    echo '<div class="error"><ul>';
    foreach ($errors as $error) {
        echo '<li>' . htmlspecialchars($error) . '</li>';
    }
    echo '</ul></div>';
}

if ($success) {
    echo '<div class="success"><p>Reward claimed successfully! Check your in-game mail.</p></div>';
}

echo '
    <form method="POST">
        <label for="char_name">Character Name:</label>
        <input type="text" id="char_name" name="char_name" required maxlength="12" value="' . htmlspecialchars($_POST['char_name'] ?? '') . '">
        
        <label for="reward_search">Search Rewards:</label>
        <input type="text" id="reward_search" placeholder="Type to filter rewards (e.g., \'Aqual\')">
        <input type="hidden" id="reward_key" name="reward_key" value="">
        
        <div id="reward-list">';

// Output categories and rewards
foreach ($categories as $category => $cat_rewards) {
    echo '<div class="category-header" onclick="toggleCategory(this)">' . htmlspecialchars($category) . '</div>';
    echo '<div class="category-content">';
    foreach ($cat_rewards as $key => $reward) {
        $full_desc = htmlspecialchars($reward['name']);
	if ($reward['type'] === 'boss_kill') {
		$req_kills = $reward['req_kills'];
		if (isset($reward['criteria_ids']) && is_array($reward['criteria_ids'])) {
			// Multiple bosses
			$boss_list = [];
			$boss_names = $reward['boss_names'] ?? $reward['criteria_ids'];
			foreach ($boss_names as $index => $boss_name) {
				if (is_string($boss_name)) {
					$boss_list[] = htmlspecialchars($boss_name) . " ($req_kills kills)";
				}
			}
			$full_desc .= " (Requires " . implode(' or ', $boss_list) . ")";
		} else {
			// Single boss (backward compatibility)
			$full_desc .= " (Requires " . number_format($req_kills) . " " . htmlspecialchars($reward['boss_name']) . " kills)";
		}
        } elseif ($reward['type'] === 'one_time_level') {
            $desc = "(One-time at level " . $reward['req_level'] . ")";
            if (isset($reward['reward_item_ids']) && count($reward['reward_item_ids']) > 0) {
                $desc .= " (Multiple items)";
            } elseif (isset($reward['stack_size'])) {
                $desc .= " (x" . $reward['stack_size'] . ")";
            } elseif (isset($reward['reward_gold'])) {
                $desc .= " (" . ($reward['reward_gold'] / 10000) . " gold)";
            }
            $full_desc .= " $desc";
        } elseif ($reward['type'] === 'daily_gift') {
            $desc = "(Daily reset at 5am EST)";
            $full_desc .= " $desc (Level-appropriate potions, mana pots, food x20)";
        }
        echo '<div class="reward-item" data-key="' . $key . '">' . $full_desc . '</div>';
    }
    echo '</div>';
}

echo '
        </div>
        
        <button type="submit" id="claim_button" disabled>Claim Reward</button>
    </form>
    
    <div class="nav">
        <a href="index.php">← Back to Registration</a> | 
        <a href="lb.php">View Leaderboard</a>
    </div>

    <script>
        function toggleCategory(header) {
            const content = header.nextElementSibling;
            content.classList.toggle("active");
        }

        const searchInput = document.getElementById("reward_search");
        const rewardList = document.getElementById("reward-list");
        const rewardItems = rewardList.getElementsByClassName("reward-item");
        const categoryContents = rewardList.getElementsByClassName("category-content");
        const rewardKeyInput = document.getElementById("reward_key");
        const claimButton = document.getElementById("claim_button");

        // Expand all categories by default
        Array.from(categoryContents).forEach(content => content.classList.add("active"));

        searchInput.addEventListener("input", function() {
            const query = this.value.trim().toLowerCase();
            Array.from(rewardItems).forEach(item => {
                const text = item.textContent.toLowerCase();
                item.style.display = query && !text.includes(query) ? "none" : "block";
                item.classList.remove("selected");
            });
            Array.from(categoryContents).forEach(content => content.classList.add("active"));
            rewardKeyInput.value = "";
            claimButton.disabled = true;
        });

        Array.from(rewardItems).forEach(item => {
            item.addEventListener("click", function() {
                Array.from(rewardItems).forEach(i => i.classList.remove("selected"));
                this.classList.add("selected");
                rewardKeyInput.value = this.getAttribute("data-key");
                claimButton.disabled = false;
            });
        });
    </script>
</body>
</html>';
?>
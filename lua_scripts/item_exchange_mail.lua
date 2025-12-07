-- Item Exchange Mail Processor
print("=======================================================")
print("[Item Exchange] Loading script...")
print("[Item Exchange] Time: " .. os.date("%Y-%m-%d %H:%M:%S"))
print("=======================================================")

local EXCHANGE_CHAR_NAME = "Exchange"
local CHECK_INTERVAL     = 10  -- seconds
local DEBUG              = false

local RATES = {}
local checkCount = 0

-- Load rates from DB
local function LoadRates()
    print("[Item Exchange] Loading rates from database...")
    RATES = {}
    
    local q = CharDBQuery("SELECT subject, give_item, give_qty, receive_item, receive_qty FROM item_exchange_rates WHERE enabled = 1")
    
    if not q then
        print("[Item Exchange] WARNING: No rates found in database")
        return false
    end
    
    local count = 0
    repeat
        local raw = q:GetString(0) or ""
        local key = string.lower(string.gsub(raw, "%s+", ""))
        RATES[key] = {
            give_item    = q:GetUInt32(1),
            give_qty     = q:GetUInt32(2),
            receive_item = q:GetUInt32(3),
            receive_qty  = q:GetUInt32(4)
        }
        print(string.format("[Item Exchange]   '%s' â %dx[%d] for %dx[%d]", 
            raw, 
            q:GetUInt32(2), q:GetUInt32(1), 
            q:GetUInt32(4), q:GetUInt32(3)))
        count = count + 1
    until not q:NextRow()
    
    print("[Item Exchange] Loaded " .. count .. " rate(s)")
    return count > 0
end

-- Process mails function
local function ProcessMails()
    checkCount = checkCount + 1
    
    if DEBUG then
        print("[Item Exchange] =======================================")
        print("[Item Exchange] CHECK #" .. checkCount .. " at " .. os.date("%H:%M:%S"))
        print("[Item Exchange] =======================================")
    end
    
    -- Reload rates from database every check (live updates!)
    LoadRates()
    
    -- Find bot character
    local bot = CharDBQuery("SELECT guid FROM characters WHERE name = '" .. EXCHANGE_CHAR_NAME .. "'")
    
    if not bot then 
        print("[Item Exchange] ERROR: Bot character '" .. EXCHANGE_CHAR_NAME .. "' not found!")
        return 
    end
    
    local botGUID = bot:GetUInt32(0)
    if DEBUG then
        print("[Item Exchange] Bot GUID: " .. botGUID)
    end

    -- Get mails with items (checked 0 or 4 = unprocessed)
    -- checked = 0: mail without items or unread
    -- checked = 4: mail with items (MAIL_CHECK_MASK_COPIED)
    -- checked = 1: marked as read (will be returned)
    -- checked = 2: already returned
    local mailQuery = string.format(
        "SELECT id, sender, subject, checked FROM mail WHERE receiver = %d AND has_items = 1 AND (checked = 0 OR checked = 4)",
        botGUID
    )
    
    local mails = CharDBQuery(mailQuery)
    
    if not mails then
        if DEBUG then
            print("[Item Exchange] No mails with items found")
        end
        return
    end

    print("[Item Exchange] *** PROCESSING MAILS ***")
    local mailCount = 0

    repeat
        mailCount = mailCount + 1
        local mail_id = mails:GetUInt32(0)
        local sender  = mails:GetUInt32(1)
        local subject = mails:GetString(2) or ""
        local checked = mails:GetUInt32(3)

        print(string.format("[Item Exchange] ----------------------------------------"))
        print(string.format("[Item Exchange] Mail #%d: ID=%d, Sender=%d, Checked=%d", mailCount, mail_id, sender, checked))
        print(string.format("[Item Exchange]   Subject: '%s'", subject))
        
        -- Normalize subject (remove spaces, lowercase)
        local subj_normalized = string.lower(string.gsub(subject, "%s+", ""))
        
        local rate = RATES[subj_normalized]
        
        if not rate then
            print("[Item Exchange]   RESULT: Invalid exchange code")
            print("[Item Exchange]   â Returning mail to sender")
            
            -- Mark as read so it gets returned to sender with items
            CharDBExecute("UPDATE mail SET checked = 1 WHERE id = " .. mail_id)
        else
            print(string.format("[Item Exchange]   Code matched! Need %dx item [%d]", 
                rate.give_qty, rate.give_item))
            
            -- Check attached items
            local itemQuery = string.format(
                "SELECT SUM(ii.count) FROM mail_items mi JOIN item_instance ii ON mi.item_guid = ii.guid WHERE mi.mail_id = %d AND ii.itemEntry = %d",
                mail_id, rate.give_item
            )
            
            local attached = 0
            local q = CharDBQuery(itemQuery)
            if q then 
                attached = q:GetUInt32(0) or 0 
            end
            
            print(string.format("[Item Exchange]   Attached: %d (need exactly %d)", attached, rate.give_qty))

            if attached ~= rate.give_qty then
                print("[Item Exchange]   RESULT: Wrong quantity")
                print("[Item Exchange]   â Returning mail to sender")
                
                -- Mark as read so it gets returned to sender with items
                CharDBExecute("UPDATE mail SET checked = 1 WHERE id = " .. mail_id)
            else
                -- SUCCESS!
                print("[Item Exchange]   RESULT: â SUCCESS! Processing exchange...")
                
                print(string.format("[Item Exchange]   â Sending %dx item [%d]", 
                    rate.receive_qty, rate.receive_item))

                -- Send reward mail
                if rate.receive_qty == 1 then
                    SendMail("Exchange Complete!", "Thank you! Trade successful.", sender, botGUID, 41, 0, 0, 0, rate.receive_item, 1)
                elseif rate.receive_qty == 2 then
                    SendMail("Exchange Complete!", "Thank you! Trade successful.", sender, botGUID, 41, 0, 0, 0, rate.receive_item, 1, rate.receive_item, 1)
                elseif rate.receive_qty == 3 then
                    SendMail("Exchange Complete!", "Thank you! Trade successful.", sender, botGUID, 41, 0, 0, 0, rate.receive_item, 1, rate.receive_item, 1, rate.receive_item, 1)
                elseif rate.receive_qty == 4 then
                    SendMail("Exchange Complete!", "Thank you! Trade successful.", sender, botGUID, 41, 0, 0, 0, rate.receive_item, 1, rate.receive_item, 1, rate.receive_item, 1, rate.receive_item, 1)
                elseif rate.receive_qty == 5 then
                    SendMail("Exchange Complete!", "Thank you! Trade successful.", sender, botGUID, 41, 0, 0, 0, rate.receive_item, 1, rate.receive_item, 1, rate.receive_item, 1, rate.receive_item, 1, rate.receive_item, 1)
                else
                    -- For larger quantities, send as one stack
                    SendMail("Exchange Complete!", "Thank you! Trade successful.", sender, botGUID, 41, 0, 0, 0, rate.receive_item, rate.receive_qty)
                end
                
                -- Delete original mail and items
                print("[Item Exchange]   â Deleting original mail")
                CharDBExecute("DELETE FROM mail_items WHERE mail_id = " .. mail_id)
                CharDBExecute("DELETE FROM mail WHERE id = " .. mail_id)

                print(string.format("[Item Exchange]   â Exchange complete for GUID %d!", sender))
            end
        end
    until not mails:NextRow()
    
    print("[Item Exchange] ========================================")
    print("[Item Exchange] Processed " .. mailCount .. " mail(s)")
    print("[Item Exchange] ========================================")
end

-- Initialize
print("[Item Exchange] Initializing...")

if not LoadRates() then
    print("[Item Exchange] WARNING: No rates loaded!")
end

print("[Item Exchange] Creating event timer...")
print("[Item Exchange] Interval: " .. CHECK_INTERVAL .. " seconds")

local eventId = CreateLuaEvent(ProcessMails, CHECK_INTERVAL * 1000, 0)

if eventId then
    print("[Item Exchange] Event created! ID: " .. tostring(eventId))
else
    print("[Item Exchange] ERROR: Failed to create event!")
end

print("=======================================================")
print("[Item Exchange] Script ACTIVE!")
print("[Item Exchange] Checking mail every " .. CHECK_INTERVAL .. " seconds")
print("[Item Exchange] Rates are loaded LIVE from database on each check")
print("=======================================================")

-- Run first check immediately
print("[Item Exchange] Running initial check...")
ProcessMails()

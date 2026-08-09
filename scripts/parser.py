import re
from datetime import datetime

class WhatsAppParser:
    def __init__(self):
        # Matches: date, time - sender: message
        # Group 1: Date (M/D/YY or MM/DD/YY or DD/MM/YY)
        # Group 2: Time (H:MM AM/PM)
        # Group 3: Sender Name
        # Group 4: Message text
        self.pattern = re.compile(r"^(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}\s?[AP]M) - (.*?): (.*)")
        
        # Matches: date, time - system message
        self.sys_pattern = re.compile(r"^(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}\s?[AP]M) - (.*)")

    def parse_file(self, file_path):
        messages = []
        current_msg = None
        line_num = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line_num += 1
                line_clean = line.rstrip('\n')
                
                # Check for standard user message
                match = self.pattern.match(line_clean)
                if match:
                    if current_msg:
                        current_msg['source_line_end'] = line_num - 1
                        self._post_process(current_msg)
                        messages.append(current_msg)
                    
                    time_str = match.group(2).replace('\u202f', ' ')
                    
                    current_msg = {
                        'timestamp_raw': f"{match.group(1)}, {time_str}",
                        'sender': match.group(3),
                        'text': match.group(4),
                        'is_system': False,
                        'is_edited': False,
                        'is_media': False,
                        'is_empty': False,
                        'source_line_start': line_num,
                        'source_line_end': line_num
                    }
                    continue
                
                # Check for system message
                match_sys = self.sys_pattern.match(line_clean)
                if match_sys:
                    if current_msg:
                        current_msg['source_line_end'] = line_num - 1
                        self._post_process(current_msg)
                        messages.append(current_msg)
                        
                    time_str = match_sys.group(2).replace('\u202f', ' ')
                    
                    current_msg = {
                        'timestamp_raw': f"{match_sys.group(1)}, {time_str}",
                        'sender': None,
                        'text': match_sys.group(3),
                        'is_system': True,
                        'is_edited': False,
                        'is_media': False,
                        'is_empty': False,
                        'source_line_start': line_num,
                        'source_line_end': line_num
                    }
                    continue
                
                # Multiline continuation
                if current_msg:
                    current_msg['text'] += '\n' + line_clean
        
        if current_msg:
            current_msg['source_line_end'] = line_num
            self._post_process(current_msg)
            messages.append(current_msg)
            
        return messages

    def _post_process(self, msg):
        # Parse datetime format MM/DD/YY, H:MM AM
        # Example: 1/2/25, 1:32 PM
        try:
            # We assume MM/DD/YY based on analysis
            dt = datetime.strptime(msg['timestamp_raw'], "%m/%d/%y, %I:%M %p")
            msg['datetime_iso'] = dt.isoformat()
        except ValueError:
            # Fallback if there are any format anomalies
            msg['datetime_iso'] = None
            
        if msg['is_system']:
            return
            
        text = msg['text']
        
        if '<This message was edited>' in text:
            msg['is_edited'] = True
            text = text.replace('<This message was edited>', '').strip()
            msg['text'] = text
            
        if '<Media omitted>' in text:
            msg['is_media'] = True
            
        if msg['text'].strip() == '':
            msg['is_empty'] = True

import re

stops_html = open('scratch/stops_markup.html', 'r', encoding='utf-8').read()

signup_path = 'signup.html'
signup_content = open(signup_path, 'r', encoding='utf-8').read()

# Pattern to replace from assignedBus select down to stopSelect end tag
old_section_pattern = re.compile(
    r'<select name="assignedBus" id="assignedBus" class="form-select">.*?</select>.*?'
    r'<select name="busName" id="busSelect" class="form-select">.*?</select>.*?'
    r'<select name="stopName" id="stopSelect" class="form-select">.*?</select>',
    re.DOTALL
)

new_section = f'''<select name="assignedBus" id="assignedBus" class="form-select">
                <option value="">— Select Assigned Bus —</option>
                <option value="rgm-1styear-001">RGM-1stYear</option>
                <option value="rgm-2ndyear-001">RGM-2ndYear</option>
                <option value="rgm-3rdyear-001">RGM-3rdYear</option>
                <option value="rgm-4thyear-001">RGM-4thYear</option>
                <option value="69134ab02313225bf5905fdc">Shantiram-45</option>
              </select>
            </div>
          </div>

          <!-- ========== USER / STUDENT FIELDS ========== -->
          <div id="user-bus-fields" class="conditional-fields">
            <div class="section-label">
              <i class="fa-solid fa-bus" style="margin-right: 4px;"></i>
              Select Your Bus & Stop
            </div>

            <div class="form-group">
              <label for="busSelect" class="form-label">Your Bus Route</label>
              <select name="busName" id="busSelect" class="form-select">
                <option value="">— Select Your Bus —</option>
                <option value="rgm-1styear-001">RGM-1stYear</option>
                <option value="rgm-2ndyear-001">RGM-2ndYear</option>
                <option value="rgm-3rdyear-001">RGM-3rdYear</option>
                <option value="rgm-4thyear-001">RGM-4thYear</option>
                <option value="69134ab02313225bf5905fdc">Shantiram-45</option>
              </select>
            </div>
          </div>

          <div id="user-stop-fields" class="conditional-fields">
            <div class="form-group">
              <label for="stopSelect" class="form-label">Your Stop</label>
              <select name="stopName" id="stopSelect" class="form-select">
                <option value="">— Select Your Stop —</option>

{stops_html}

              </select>'''

if not old_section_pattern.search(signup_content):
    print("ERROR: Pattern not found in signup.html!")
else:
    updated_content = old_section_pattern.sub(new_section, signup_content)
    open(signup_path, 'w', encoding='utf-8').write(updated_content)
    print("SUCCESS: signup.html updated with RGM-1stYear, RGM-2ndYear, RGM-3rdYear, RGM-4thYear!")

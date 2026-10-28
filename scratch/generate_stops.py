stops = [
    'KondaReddy Fort', 'Control Room', 'Sv Complex', 'Railway Station Road',
    'Rajhvihar', 'Kurnool Medical College', 'Collector Office', 'Gayathri Estates',
    'Maddur Nagar', 'C Camp', 'Amma Hospital', 'Nandyal Checkpost',
    'Maruthi Mega City', 'G. Pullareddy Engineering College', 'B. Thandrapadu',
    'B. Thandrapadu Lake View', 'Raaga Mayuri Resorts', 'Nannur', 'RGM College'
]

routes = [
    ('RGM-1stYear', 'rgm-1styear-001', 'rgm1y'),
    ('RGM-2ndYear', 'rgm-2ndyear-001', 'rgm2y'),
    ('RGM-3rdYear', 'rgm-3rdyear-001', 'rgm3y'),
    ('RGM-4thYear', 'rgm-4thyear-001', 'rgm4y'),
]

out = []
for r_name, r_id, pfx in routes:
    out.append(f'                <!-- ===== {r_name} Stops ===== -->')
    for i, s in enumerate(stops, start=1):
        out.append(f'                <option value="{pfx}-stop-{i:02d}" data-bus="{r_id}">{s}</option>')

# Also Shantiram-45
out.append('                <!-- ===== Shantiram-45 Stops ===== -->')
for i, s in enumerate(stops[:10], start=1):
    out.append(f'                <option value="sr45-stop-{i:02d}" data-bus="69134ab02313225bf5905fdc">{s}</option>')

with open('scratch/stops_markup.html', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))

print(f"Generated {len(out)} lines of stops markup.")

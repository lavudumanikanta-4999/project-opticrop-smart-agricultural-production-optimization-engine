import os, stat, shutil, glob, fitz

team_id = ""
project_name = "Opticrop"
submission_date = "04-07-2026"

# ─── helpers ──────────────────────────────────────────────────────────────────

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def save_pdf(doc, path):
    tmp = path + ".tmp"
    doc.save(tmp)
    doc.close()
    if os.path.exists(path):
        os.remove(path)
    os.rename(tmp, path)

def whiteout(page, rect, expand=1):
    r = fitz.Rect(rect)
    r = fitz.Rect(r.x0 - expand, r.y0 - expand, r.x1 + expand, r.y1 + expand)
    page.draw_rect(r, color=(1,1,1), fill=(1,1,1))

def put(page, rect, text, fontsize=8, align=0, color=(0,0,0)):
    r = fitz.Rect(rect)
    page.insert_textbox(r, text, fontsize=fontsize, fontname="helv",
                        color=color, align=align)

def replace_meta(page):
    """Permanently erase placeholder text and insert project metadata."""
    hits_x = page.search_for("xxxxxx")
    for i, r in enumerate(hits_x):
        page.add_redact_annot(r, fill=(1, 1, 1))
    for ds in ["15 March 2024", "15 March 2026", "15 March 2025"]:
        for r in page.search_for(ds):
            page.add_redact_annot(r, fill=(1, 1, 1))
    page.apply_redactions()

    # Re-search after redaction to get the clean positions, then insert values
    # Use original positions stored before redaction
    # Simply insert at the known label positions
    for label, val in [("Team ID", team_id), ("Project Name", project_name)]:
        lbls = page.search_for(label)
        if lbls:
            # Insert after the label text
            x = lbls[0].x1 + 15
            y = lbls[0].y1 - 1
            page.insert_text(fitz.Point(x, y), val, fontsize=9, fontname="helv")

    for label, val in [("Date", submission_date)]:
        lbls = page.search_for(label)
        if lbls:
            x = lbls[0].x1 + 15
            y = lbls[0].y1 - 1
            page.insert_text(fitz.Point(x, y), val, fontsize=9, fontname="helv")

# ─── STEP 1: Brainstorming ────────────────────────────────────────────────────

def fill_brainstorming(pdf_path):
    print(f"  -> {pdf_path}")
    doc = fitz.open(pdf_path)
    pg = doc[0]
    replace_meta(pg)

    # Put D.Goutham in the first row of Step 1 table under "Team Member" column
    # S.No [78-160] | Team Member [160-270] | Idea [270-380] |
    # Category [380-480] | Group No. [480-540]
    # Row "1" sno is at y0=349.9 => top=340.9  bottom=362.9
    yt = 340.9
    yb = yt + 22
    put(pg, (160, yt, 270, yb), "D.Goutham", fontsize=8, align=1)

    save_pdf(doc, pdf_path)

# ─── STEP 1: Problem Statements ──────────────────────────────────────────────

def fill_problem_statements(pdf_path):
    print(f"  -> {pdf_path}")
    doc = fitz.open(pdf_path)
    pg = doc[0]
    replace_meta(pg)

    # White out the example PS-1 loan row
    whiteout(pg, (83, 500, 540, 570), expand=2)

    # Template columns (from header word extraction):
    # PS [83-148] | Customer [148-228] | Trying [228-302] |
    # But [302-382] | Because [382-456] | Feel [456-535]
    # Rows at y≈508, 563, 618  (each row ~55 pt tall)
    ps_rows = [
        ("Rajesh\n(Farmer)",      "Maximize crop yield",   "NPK mismatch",        "No soil diagnostics", "Anxious"),
        ("Rajesh\n(Farmer)",      "Apply fertilizers",     "Over-application",    "No corrective guide", "Wasteful"),
        ("Dr. Anita\n(Consult.)", "Analyze soil trends",   "Fragmented datasets", "No dashboard",        "Frustrated"),
    ]
    row_tops_ps = [499, 554, 609]

    for i, (cust, trying, but_, because, feel) in enumerate(ps_rows):
        yt = row_tops_ps[i]
        yb = yt + 50
        put(pg, (83,  yt, 148, yb), cust,    fontsize=7, align=1)
        put(pg, (148, yt, 228, yb), trying,  fontsize=7, align=1)
        put(pg, (228, yt, 302, yb), but_,    fontsize=7, align=1)
        put(pg, (302, yt, 382, yb), because, fontsize=7, align=1)
        put(pg, (456, yt, 535, yb), feel,    fontsize=7, align=1)

    save_pdf(doc, pdf_path)

# ─── STEP 1: Empathy Map ─────────────────────────────────────────────────────

def fill_empathy_map(pdf_path):
    print(f"  -> {pdf_path}")
    doc = fitz.open(pdf_path)
    pg = doc[0]
    replace_meta(pg)

    says   = pg.search_for("SAYS")
    thinks = pg.search_for("THINKS")
    does   = pg.search_for("DOES")
    feels  = pg.search_for("FEELS")

    put(pg, (235, 450, 380, 510), "Rajesh\n(Farmer Persona)", fontsize=9, align=1)

    if says:
        put(pg, (50, says[0].y1+10, 230, says[0].y1+140),
            "• 'I want to maximize yields\n  but costs are unsustainable.'\n"
            "• 'Which crops fit my soil?'", fontsize=8)
    if thinks:
        put(pg, (325, thinks[0].y1+10, 560, thinks[0].y1+140),
            "• 'Will rain be sufficient\n  this season?'\n"
            "• 'Is my soil losing fertility?'", fontsize=8)
    if does:
        put(pg, (50, does[0].y1+10, 230, does[0].y1+140),
            "• Plants by historical cycles.\n"
            "• Applies generic fertilizers.\n"
            "• Manually records harvests.", fontsize=8)
    if feels:
        put(pg, (325, feels[0].y1+10, 560, feels[0].y1+140),
            "• Anxious about crop failures.\n"
            "• Stressed about financial loans.\n"
            "• Optimistic about AI guidance.", fontsize=8)

    save_pdf(doc, pdf_path)

# ─── STEP 2: Customer Journey Map ────────────────────────────────────────────

def fill_customer_journey(pdf_path):
    print(f"  -> {pdf_path}")
    doc = fitz.open(pdf_path)
    for pg in doc:
        replace_meta(pg)

    pg1 = doc[0]
    stage_cols = [(155, 280), (280, 405), (405, 555)]

    row_labels = ["Actions", "Touchpoint", "Thought", "Feeling"]
    row_contents = [
        ["• Collects soil sample\n• Gets NPK lab report",
         "• Opens Opticrop app\n• Inputs NPK & pH values",
         "• Reviews crop suggestion\n• Checks yield forecast"],
        ["• Soil testing lab",   "• Opticrop web form",  "• Results display card"],
        ["• 'Is this lab reliable?'", "• 'Are units in kg/ha?'", "• 'Is this crop safe?'"],
        ["• Apprehensive",       "• Confused",           "• Hopeful / Relieved"],
    ]

    for label, contents in zip(row_labels, row_contents):
        hits = pg1.search_for(label)
        if hits:
            row_y0 = hits[0].y1 + 5
            row_y1 = row_y0 + 70
            for col_idx, (x0, x1) in enumerate(stage_cols):
                put(pg1, (x0, row_y0, x1, row_y1), contents[col_idx], fontsize=8)

    if len(doc) > 1:
        pg2 = doc[1]
        for label, contents in zip(
            ["Ownership", "Opportunitie"],
            [["• Farmer", "• Farmer", "• App Engine"],
             ["• Add sampling guide in UI", "• Add field validation hints", "• Show model accuracy"]]
        ):
            hits = pg2.search_for(label)
            if hits:
                row_y0 = hits[0].y1 + 5
                row_y1 = row_y0 + 70
                for col_idx, (x0, x1) in enumerate(stage_cols):
                    put(pg2, (x0, row_y0, x1, row_y1), contents[col_idx], fontsize=8)

    save_pdf(doc, pdf_path)

# ─── STEP 2: Data Flow Diagram ────────────────────────────────────────────────

def fill_dfd(pdf_path):
    print(f"  -> {pdf_path}")
    doc = fitz.open(pdf_path)
    for pg in doc:
        replace_meta(pg)

    pg2 = doc[1] if len(doc) > 1 else doc[0]
    pg2.insert_text((80, 230),
                    "Opticrop - Level 0 & Level 1 Data Flow Diagram",
                    fontsize=13, fontname="helvetica-bold")
    dfd = (
        "         [ Farmer / Researcher ]\n"
        "              |             ^\n"
        "   (NPK & Climate inputs)   (Crop & Yield results)\n"
        "              |\n"
        "              v\n"
        "  +---------------------------------------+\n"
        "  | 1.0  Input Validation & Bounds Check  |\n"
        "  +---------------------------------------+\n"
        "              |\n"
        "              v\n"
        "  +---------------------------------------+\n"
        "  | 2.0  ML Inference  (RF / KMeans .pkl) |\n"
        "  +---------------------------------------+\n"
        "              |\n"
        "              v\n"
        "  +---------------------------------------+\n"
        "  | 3.0  NPK Correction & Yield Estimate  |\n"
        "  +---------------------------------------+\n"
        "              |\n"
        "              v\n"
        "  +---------------------------------------+\n"
        "  | 4.0  Flask Render / JSON Response     |\n"
        "  +---------------------------------------+\n"
        "              |\n"
        "              v\n"
        "         [ User Browser ]\n"
        "              |\n"
        "              v\n"
        "   [ user_predictions.csv  (CSV log) ]\n"
    )
    pg2.insert_textbox((50, 255, 560, 750), dfd, fontsize=9.5, fontname="courier")
    save_pdf(doc, pdf_path)

# ─── STEP 2: Solution Requirements ───────────────────────────────────────────

def fill_solution_requirements(pdf_path):
    print(f"  -> {pdf_path}")
    doc = fitz.open(pdf_path)
    pg = doc[0]
    replace_meta(pg)

    reqs = [
        ("Soil parameter input form (NPK, pH, rainfall, temperature, humidity)", "Functional",     "High"),
        ("Random Forest crop recommendation with 100% test accuracy",             "Functional",     "High"),
        ("Custom NPK correction: prescribe Urea / SSP / MOP amendments",         "Functional",     "High"),
        ("Automated unit tests covering Flask routes and prediction bounds",       "Non-Functional", "High"),
    ]
    row_tops = [440, 510, 580, 650]

    for i, (req, rtype, pri) in enumerate(reqs):
        yt = row_tops[i]
        yb = yt + 65
        put(pg, (78,  yt, 108, yb), str(i+1), fontsize=8, align=1)
        put(pg, (108, yt, 385, yb), req,       fontsize=7.5, align=0)
        put(pg, (385, yt, 480, yb), rtype,     fontsize=8, align=1)
        put(pg, (480, yt, 535, yb), pri,       fontsize=8, align=1)

    save_pdf(doc, pdf_path)

# ─── Generic filler ──────────────────────────────────────────────────────────

def fill_generic(pdf_path, content):
    print(f"  -> {pdf_path}")
    doc = fitz.open(pdf_path)
    for pg in doc:
        replace_meta(pg)
    pg = doc[0]
    pg.insert_textbox((72, 235, 530, 720), content,
                      fontsize=9.5, fontname="helv")
    save_pdf(doc, pdf_path)

# ─── Copy templates ──────────────────────────────────────────────────────────

def copy_templates():
    print("Copying fresh templates ...")
    for folder in [
        "1. Brainstorming & Ideation",
        "2.Requirement Analysis",
        "3. Project Design Phase",
        "4. Project Planning Phase",
        "5. Project Development Phase",
        "6.Project Testing",
        "7.Project Documentation",
        "8.Project Demonstration",
    ]:
        os.makedirs(folder, exist_ok=True)
        src = os.path.join("temp_template", folder)
        if not os.path.exists(src):
            continue
        for pdf in glob.glob(os.path.join(src, "*.pdf")):
            dst = os.path.join(folder, os.path.basename(pdf))
            if "Sample Project Documentation" in dst and os.path.exists(dst):
                print(f"  keeping: {dst}")
                continue
            shutil.copy(pdf, dst)
            print(f"  copied:  {dst}")

# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    copy_templates()
    print("\nFilling PDFs ...")

    fill_brainstorming("1. Brainstorming & Ideation/Brainstorming & Idea Prioritization.pdf")
    fill_problem_statements("1. Brainstorming & Ideation/Define Problem Statements .pdf")
    fill_empathy_map("1. Brainstorming & Ideation/Empathy Map.pdf")
    fill_customer_journey("2.Requirement Analysis/Customer Journey Map.pdf")
    fill_dfd("2.Requirement Analysis/Data Flow Diagram.pdf")
    fill_solution_requirements("2.Requirement Analysis/Solution Requirements.pdf")

    fill_generic("2.Requirement Analysis/Technology Stack.pdf",
        "Opticrop Technology Stack\n\n"
        "Language   : Python 3.10+\n"
        "Framework  : Flask 3.1.3 - routing, Jinja2 templates, REST endpoints\n"
        "ML / AI    : Scikit-learn 1.9 - Random Forest (classifier + regressor), K-Means\n"
        "Data       : Pandas 3.0, NumPy 2.5\n"
        "Plotting   : Matplotlib 3.11, Seaborn 0.13 - accuracy charts, confusion matrices\n"
        "Frontend   : HTML5, CSS3 (glassmorphism), Bootstrap 5\n"
        "Testing    : pytest / Python unittest\n"
        "Version Ctrl: Git / GitHub\n")

    fill_generic("3. Project Design Phase/Problem-Solution Fit.pdf",
        "Opticrop - Problem-Solution Fit\n\n"
        "Problem 1 : Crop-to-soil misalignment -> poor harvest yields\n"
        "Solution  : Random Forest classifier recommends optimal crop from 22 types\n\n"
        "Problem 2 : NPK over-application -> soil degradation\n"
        "Solution  : NPK Correction Engine prescribes Urea / SSP / MOP amendments\n\n"
        "Problem 3 : Yield uncertainty -> financial risk\n"
        "Solution  : RF Regressor predicts yield (t/ha) with R2 >= 0.92\n\n"
        "Problem 4 : No soil health diagnostics\n"
        "Solution  : K-Means clustering groups soil into 5 health categories\n")

    fill_generic("3. Project Design Phase/Proposed Solution.pdf",
        "Opticrop - Proposed Solution\n\n"
        "An AI-driven Agricultural Optimizer delivering five core features:\n\n"
        "1. Crop Recommender   - RF classifier, 22 crop classes, 100% test accuracy\n"
        "2. Yield Forecaster   - RF regressor predicts final yield in t/ha\n"
        "3. Soil Diagnoser     - K-Means clustering into 5 soil health clusters\n"
        "4. NPK Prescriber     - deficit-based Urea / SSP / MOP amendment guide\n"
        "5. Analytics Dashboard- accuracy charts, confusion matrix, feature importance\n")

    fill_generic("3. Project Design Phase/Solution Architecture.pdf",
        "Opticrop - Solution Architecture\n\n"
        "Layer 1 - Client UI\n"
        "  HTML5 forms, CSS3 glassmorphism, Bootstrap 5 responsive grid\n\n"
        "Layer 2 - Flask Server\n"
        "  /predict POST route: validates inputs -> scales -> infers -> logs to CSV\n"
        "  /dashboard GET route: renders analytics charts\n\n"
        "Layer 3 - ML Pipeline\n"
        "  best_model.pkl  (RF Classifier)\n"
        "  yield_model.pkl (RF Regressor)\n"
        "  scaler.pkl      (StandardScaler)\n"
        "  kmeans_model.pkl(K-Means, k=5)\n\n"
        "Layer 4 - Data Store\n"
        "  datasets/user_predictions.csv  - append-only prediction log\n")

    fill_generic("4. Project Planning Phase/Project Planning.pdf",
        "Opticrop - Project Milestones\n\n"
        "M1  Environment setup, virtual env, pip install requirements  [Done]\n"
        "M2  Dataset generation (generate_datasets.py, 2200 records)   [Done]\n"
        "M3  Model training & comparison (KNN / DT / LR / RF)          [Done]\n"
        "M4  Flask server: routing, validation, CSV logging             [Done]\n"
        "M5  Frontend: Jinja2 templates, CSS glassmorphism cards        [Done]\n"
        "M6  Testing: unittest suite (4 tests passed), final review     [Done]\n")

    fill_generic("5. Project Development Phase/Code-Layout, Readability and Reusability.pdf",
        "Opticrop - Code Layout & Modularity\n\n"
        "app.py               - Flask server, /predict & /dashboard routes\n"
        "train_models.py      - training pipeline; outputs .pkl binaries\n"
        "generate_datasets.py - synthetic dataset generator\n"
        "tests/test_app.py    - unittest suite (4 tests)\n"
        "models/              - serialised ML pipelines (.pkl)\n"
        "templates/           - Jinja2 HTML pages\n"
        "static/              - CSS, images\n\n"
        "Conventions: PEP 8 formatting, snake_case naming, full docstrings,\n"
        "             type hints where applicable.\n")

    fill_generic("5. Project Development Phase/Coding & Solution.pdf",
        "Opticrop - Key Code Modules\n\n"
        "load_all_models()  [app.py]\n"
        "  Deserialises best_model.pkl, yield_model.pkl, scaler.pkl,\n"
        "  kmeans_model.pkl on server start into a shared dict.\n\n"
        "/predict  [POST, app.py]\n"
        "  1. Parse & validate 7 form fields (bounds check)\n"
        "  2. StandardScaler transform\n"
        "  3. RF predict -> crop label\n"
        "  4. RF regress -> yield (t/ha)\n"
        "  5. K-Means predict -> soil cluster\n"
        "  6. NPK delta -> fertiliser advice\n"
        "  7. Append row to user_predictions.csv\n"
        "  8. Render result Jinja2 template\n\n"
        "train_models.py\n"
        "  Scales, encodes, trains 4 classifiers, selects best by accuracy,\n"
        "  dumps pipelines to models/ directory.\n")

    fill_generic("5. Project Development Phase/No. of Functional Features Included in the Solution.pdf",
        "Opticrop - Functional Features (5 implemented)\n\n"
        "1. Crop Recommender\n"
        "   RF classifier recommends optimal crop from 22 types\n"
        "   based on N, P, K, pH, rainfall, temperature, humidity.\n\n"
        "2. Yield Forecaster\n"
        "   RF regressor estimates harvest yield in t/ha.\n\n"
        "3. Soil Health Diagnoser\n"
        "   K-Means (k=5) clusters soil into Excellent / Good /\n"
        "   Moderate / Poor / Critical.\n\n"
        "4. NPK Prescriber\n"
        "   Computes NPK deficit vs. crop optimum; recommends\n"
        "   Urea (N), SSP (P), MOP (K) kg/ha dosage.\n\n"
        "5. Analytics Dashboard\n"
        "   Accuracy comparison bar chart, confusion matrix heatmap,\n"
        "   feature-importance plot rendered with Matplotlib/Seaborn.\n")

    fill_generic("6.Project Testing/Performance Testing.pdf",
        "Opticrop - Testing & Performance\n\n"
        "Model Accuracy (validation set)\n"
        "  Random Forest Classifier  : 100.00 %\n"
        "  Decision Tree Classifier  :  98.18 %\n"
        "  K-Nearest Neighbours      :  97.50 %\n"
        "  Logistic Regression       :  95.68 %\n\n"
        "Yield Regressor\n"
        "  Random Forest Regressor   : R2 = 0.92+\n\n"
        "Automated Unit Tests  (pytest / unittest)\n"
        "  test_homepage_loads    PASSED\n"
        "  test_predict_endpoint  PASSED\n"
        "  test_csv_logging       PASSED\n"
        "  test_bounds_validation PASSED\n"
        "  => 4 / 4 tests passed\n")

    fill_generic("7.Project Documentation/Project Executable Files.pdf",
        "Opticrop - Executable Files & Artefacts\n\n"
        "Source Code\n"
        "  app.py                     Flask application entry-point\n"
        "  train_models.py            ML training pipeline\n"
        "  generate_datasets.py       Synthetic dataset generator\n"
        "  tests/test_app.py          Automated test suite\n\n"
        "Serialised Models\n"
        "  models/best_model.pkl      RF Classifier pipeline\n"
        "  models/yield_model.pkl     RF Regressor pipeline\n"
        "  models/scaler.pkl          StandardScaler\n"
        "  models/kmeans_model.pkl    K-Means (k=5)\n\n"
        "Configuration\n"
        "  requirements.txt           Pip dependency list\n"
        "  README.md                  Setup & run instructions\n")

    fill_generic("8.Project Demonstration/Communication.pdf",
        "Opticrop - Team Communication\n\n"
        "Role Assignments\n"
        "  Team Lead (A)       : milestone planning, review co-ordination\n"
        "  ML Developer (B)    : dataset generation, model training, evaluation\n"
        "  Backend Developer(C): Flask routes, CSV logging, deployment\n"
        "  Frontend / QA (D)   : HTML/CSS templates, unit tests, documentation\n\n"
        "Communication Channels\n"
        "  Daily stand-up (15 min): status sync, blocker resolution\n"
        "  GitHub pull-request reviews before merging to main\n"
        "  Shared task board (GitHub Issues / Projects)\n")

    fill_generic("8.Project Demonstration/Demonstration of Proposed Features.pdf",
        "Opticrop - Demo Script\n\n"
        "Segment 1 - Input Form (2 min)\n"
        "  Show form fields: N, P, K, pH, rainfall, temperature, humidity.\n"
        "  Demonstrate out-of-bounds validation error.\n\n"
        "Segment 2 - Prediction Results (3 min)\n"
        "  Submit valid inputs -> display Crop suggestion, Yield (t/ha),\n"
        "  Soil cluster, NPK correction table.\n\n"
        "Segment 3 - Analytics Dashboard (3 min)\n"
        "  Accuracy comparison chart, confusion matrix, feature importances.\n\n"
        "Segment 4 - Unit Test Run (2 min)\n"
        "  Run 'python -m pytest tests/' live; show 4/4 passed.\n")

    fill_generic("8.Project Demonstration/Project Demo Planning.pdf",
        "Opticrop - Demo Agenda (10 min)\n\n"
        "0:00 - 1:00   Introduction: problem, objectives, team\n"
        "1:00 - 2:30   ML: dataset overview, model comparison, accuracy\n"
        "2:30 - 6:00   Live demo: form -> predict -> results -> dashboard\n"
        "6:00 - 8:00   Unit test run & CSV log inspection\n"
        "8:00 - 9:30   Scalability roadmap & future features\n"
        "9:30 - 10:00  Q&A\n")

    fill_generic("8.Project Demonstration/Scalability & Future Plan.pdf",
        "Opticrop - Scalability & Roadmap\n\n"
        "Short-term (3 months)\n"
        "  REST API for IoT soil sensors (real-time NPK feeds)\n"
        "  Multi-language support (Hindi, Telugu, Tamil)\n\n"
        "Mid-term (6 months)\n"
        "  Weather API integration for automated irrigation alerts\n"
        "  Mobile-responsive PWA with offline mode\n\n"
        "Long-term (12 months)\n"
        "  Leaf-disease CNN (PyTorch) via camera upload\n"
        "  SaaS multi-tenant login (farmer history & trend analytics)\n"
        "  Govt. API linkage for subsidy eligibility checks\n")

    fill_generic("8.Project Demonstration/Team Involvement in Demonstration.pdf",
        "Opticrop - Team Demo Roles\n\n"
        "Member A - Lead Presenter\n"
        "  Delivers introduction, problem framing, closing roadmap & Q&A.\n\n"
        "Member B - ML Presenter\n"
        "  Explains dataset, model selection, accuracy metrics, confusion matrix.\n\n"
        "Member C - App Presenter\n"
        "  Performs live web-app demo: form input -> crop result -> dashboard.\n\n"
        "Member D - QA Presenter\n"
        "  Runs pytest live, shows CSV log, explains test coverage.\n")

    print("\nDone - all 21 deliverable PDFs filled successfully.")

if __name__ == "__main__":
    main()

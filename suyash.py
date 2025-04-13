import gradio as gr
import google.generativeai as genai
from fpdf import FPDF
from datetime import datetime
import os

# === Configure Gemini API ===
genai.configure(api_key="AIzaSyABjjtDkWlJTGYgy5mkagHlDAEhpPTm1JI")
model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

# === Track Past Applications ===
app_history = []

# === PDF Generator ===
def generate_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)
    filename = f"Internship_Application_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf.output(filename)
    return filename

# === Main Function ===
def generate_application(name, degree, specialization, skills, experience, company, role, tone):
    prompt = (
        f"You are a professional career writing assistant. Craft a compelling, well-structured internship application letter.\n"
        f"Candidate Details:\n"
        f"Name: {name}\nDegree: {degree}\nSpecialization: {specialization}\n"
        f"Skills: {skills}\nExperience: {experience}\n"
        f"Target Company: {company}\nRole: {role}\nTone: {tone.lower()}\n\n"
        f"Write a personalized letter including:\n"
        f"- A professional introduction\n- Motivation for applying\n"
        f"- Relevant strengths\n- Fit for the role & company\n- Gratitude & closing\n"
    )

    try:
        response = model.generate_content(prompt)
        letter = response.text.strip()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        app_history.append(f"[{timestamp}] {name} → {role} at {company}")
        history_text = "\n".join(app_history[-5:])

        pdf_path = generate_pdf(letter)
        return letter, history_text, pdf_path
    except Exception as e:
        return f"Error: {str(e)}", "", None

# === Reset Everything ===
def reset():
    app_history.clear()
    return "", "", None

# === Gradio App UI ===
with gr.Blocks(theme=gr.themes.Soft()) as app:
    gr.Markdown("""
        <div style="text-align: center; padding: 20px;">
            <h1 style="font-size: 2.5rem;">Engineering Internship Application Generator</h1>
            <p style="color: gray; font-size: 1.1rem;">
                Generate a professional, AI-powered internship cover letter and download it as a PDF.
            </p>
        </div>
    """)

    with gr.Row():
        with gr.Column(scale=3):
            name = gr.Textbox(label="Full Name")
            degree = gr.Textbox(label="Degree (e.g., B.Tech, M.Tech)")
            specialization = gr.Textbox(label="Specialization (e.g., Civil, CSE, Mechanical)")
            skills = gr.Textbox(label="Skills (comma separated)")
            experience = gr.Textbox(label="Relevant Experience")
            company = gr.Textbox(label="Target Company")
            role = gr.Textbox(label="Internship Role")
            tone = gr.Radio(["Formal", "Confident", "Friendly"], label="Tone Style", value="Formal")
            generate_btn = gr.Button("Generate Cover Letter")
        with gr.Column(scale=2):
            output = gr.Textbox(label="AI-Generated Cover Letter", lines=20)
            history = gr.Textbox(label="Recent Applications", lines=6, interactive=False)
            pdf_file = gr.File(label="Download PDF File")
            reset_btn = gr.Button("Reset")

    generate_btn.click(
        fn=generate_application,
        inputs=[name, degree, specialization, skills, experience, company, role, tone],
        outputs=[output, history, pdf_file]
    )

    reset_btn.click(fn=reset, outputs=[output, history, pdf_file])

app.launch()

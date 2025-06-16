import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext,messagebox
from datetime import datetime
import os
import subprocess
import threading


class AITestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Test Scenario Generator")
        available_models = self.get_installed_models()
        self.model_var = tk.StringVar(value=available_models[0] if available_models else "")
        self.automation_model_var = tk.StringVar(value=available_models[0] if available_models else "")
        self.test_name_var = tk.StringVar()
        self.uploaded_files = []
        self.generated_response = ""
        self.generated_code = ""
        self.source_type_var = tk.StringVar(value="code")
        self.create_widgets()
        
    def get_installed_models(self):
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            lines = result.stdout.strip().split("\n")[1:]
            models = [line.split()[0] for line in lines if line.strip()]
            return models or ["No models found"]
        except Exception as e:
            print(f"Error reading models: {e}")
            return ["No models found"]    

    def create_widgets(self):
        self.tab_control = ttk.Notebook(self.root)

        self.tab1 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab1, text="1. Files & Model")
        self.create_tab1()

        self.tab2 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab2, text="2. Test Scenarios")
        self.create_tab2()

        self.tab3 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab3, text="3. Automation Code")
        self.create_tab3()

        self.tab_control.pack(expand=1, fill="both")

    def create_tab1(self):
        frame = self.tab1
        ttk.Label(frame, text="Select AI Model:").pack(anchor="w", padx=10, pady=(10, 2))
        model_list = self.get_installed_models()
        self.model_menu = ttk.Combobox(frame, textvariable=self.model_var, values=model_list, state="readonly")
        self.model_menu.pack(fill="x", padx=10)

        ttk.Label(frame, text="Test Name:").pack(anchor="w", padx=10, pady=(10, 2))
        self.test_name_entry = ttk.Entry(frame, textvariable=self.test_name_var)
        self.test_name_entry.pack(fill="x", padx=10)

        ttk.Label(frame, text="Source Type:").pack(anchor="w", padx=10, pady=(10, 2))
        source_options = [("Code Only", "code"), ("Analysis Document Only", "analysis"), ("Both", "both")]
        for label, value in source_options:
            ttk.Radiobutton(frame, text=label, variable=self.source_type_var, value=value, command=self.update_prompt).pack(anchor="w", padx=20)

        self.add_button = ttk.Button(frame, text="Add Files", command=self.add_files)
        self.add_button.pack(padx=10, pady=(10, 2))

        self.file_listbox = tk.Listbox(frame, height=6)
        self.file_listbox.pack(fill="both", padx=10, pady=2, expand=True)

        self.remove_button = ttk.Button(frame, text="Remove Selected File", command=self.remove_selected_file)
        self.remove_button.pack(padx=10, pady=(2, 10))

        self.prompt_text = scrolledtext.ScrolledText(frame, height=10)
        self.prompt_text.pack(padx=10, pady=5, fill="both")

        self.generate_button = ttk.Button(frame, text="Generate Test Scenarios", command=self.generate_scenarios)
        self.generate_button.pack(pady=5)

        self.status_label = ttk.Label(frame, text="")
        self.status_label.pack()

        self.update_prompt()

    def create_tab2(self):
        frame = self.tab2
        self.response_area = scrolledtext.ScrolledText(frame, height=25)
        self.response_area.pack(padx=10, pady=(10, 5), fill="both")
        self.save_and_continue_button = ttk.Button(frame, text="Save & Continue to Automation", command=self.save_and_continue)
        self.save_and_continue_button.pack(pady=(0, 10))

    def create_tab3(self):
        frame = self.tab3
        ttk.Label(frame, text="Select AI Model for Automation:").pack(anchor="w", padx=10, pady=(10, 2))
        model_list = self.get_installed_models()
        self.automation_model_menu = ttk.Combobox(frame, textvariable=self.automation_model_var, values=model_list, state="readonly")
        self.automation_model_menu.pack(fill="x", padx=10)

        self.automation_prompt = scrolledtext.ScrolledText(frame, height=10)
        self.automation_prompt.pack(padx=10, pady=(10, 5), fill="both")

        self.update_automation_prompt()

        self.generate_automation_button = ttk.Button(frame, text="Generate Automation Code", command=self.generate_automation)
        self.generate_automation_button.pack(pady=5)

        self.automation_status_label = ttk.Label(frame, text="")
        self.automation_status_label.pack()

        self.automation_code = scrolledtext.ScrolledText(frame, height=15)
        self.automation_code.pack(padx=10, pady=(5, 5), fill="both")

        self.save_code_button = ttk.Button(frame, text="Save Automation Code", command=self.save_automation_code)
        self.save_code_button.pack(pady=(0, 10))    
        
        self.automation_start_time = None
        
        
    def update_automation_prompt(self):
        choice = self.source_type_var.get()
        self.automation_prompt.delete("1.0", tk.END)
        if choice == "analysis":
            self.automation_prompt.insert("1.0",
                "⚠️ Automation Not Available\n\n"
                "Automation code cannot be generated from analysis documentation only.\n"
                "Please include source code files as well to enable automation script generation."
            )
        else:
            self.automation_prompt.insert("1.0",
                "You are a senior QA automation engineer.\n\n"
                "You are given:\n"
                "- The source code files of a web application (frontend and backend)\n"
                "- A set of test scenarios written from the user's perspective\n"
                "- (Optional) Analysis or design documentation\n\n"
                "Your task:\n\n"
                "Write complete, high-quality Playwright automation tests in **TypeScript** that:\n"
                "1. Follow the official @playwright/test format\n"
                "2. Include meaningful test() blocks with descriptive titles\n"
                "3. Contain expect() assertions that fully validate UI behavior and logic\n"
                "4. Cover:\n"
                "   - Happy paths (successful flows)\n"
                "   - Edge cases (invalid inputs, boundary values)\n"
                "   - Negative flows (failed login, empty fields)\n"
                "   - Optional conditions (user cancels, prompt is dismissed)\n\n"
                "Additional Instructions:\n"
                "- Maximize code coverage across all components and logic in the source code\n"
                "- Use element selectors that reflect the actual HTML structure\n"
                "- Group related tests logically in the same file\n"
                "- Keep the code clean and directly executable in a standard Playwright project"
            )
        
        # Link to radio buttons
        for child in self.tab1.winfo_children():
            if isinstance(child, ttk.Radiobutton):
                child.config(command=lambda: [self.update_prompt(), self.update_automation_prompt()])    
                

    def generate_automation(self):
        if self.source_type_var.get() == "analysis":
            messagebox.showwarning(
                "Automation Not Available",
                "Automation code cannot be generated from analysis documentation only.\n\nPlease include source code files as well."
            )
            return
        self.set_automation_start_time()
        #self.generate_automation_button.config(state="disabled")
        self.toggle_controls(state="disable")
        #self.tab_control.tab(index, state='disabled')
        self.automation_status_label.config(text=f"{self.automation_start_time} ⏳ Generating automation code...")
        thread = threading.Thread(target=self.run_automation_inference)
        thread.start()

    def run_automation_inference(self):
        prompt = self.automation_prompt.get("1.0", tk.END).strip()
        model = self.automation_model_var.get()
        #files = "\n".join(self.uploaded_files)
        file_contents = ""
        for filepath in self.uploaded_files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    file_contents += f"\n\n--- File: {os.path.basename(filepath)} ---\n"
                    file_contents += f.read()
            except Exception as e:
                file_contents += f"\n\n--- File: {os.path.basename(filepath)} (Error reading file: {e}) ---\n"
                
        scenarios = self.generated_response
        full_prompt = f"{prompt}\n\nTest Scenarios:\n{scenarios}\n\nSource Files:\n{file_contents}"

        try:
            result = subprocess.run(["ollama", "run", model], input=full_prompt.encode("utf-8"), capture_output=True)
            response = result.stdout.decode("utf-8").strip() if result.returncode == 0 else result.stderr.decode("utf-8").strip()
        except Exception as e:
            response = f"Error while calling model: {str(e)}"

        self.automation_code.after(0, lambda: self.display_automation_code(response))
        
    def set_automation_start_time(self):
        self.automation_start_time = datetime.now().strftime("%H:%M")

    def display_automation_code(self, code):
        
        self.generated_code = code
        self.automation_code.delete("1.0", tk.END)
        self.automation_code.insert("1.0", code)
        end_time = datetime.now().strftime("%H:%M")
        self.automation_status_label.config(text=f"{self.automation_start_time} → {end_time} Automation code generated.")
        #self.generate_automation_button.config(state="normal")
        self.toggle_controls(state="normal")

    def save_automation_code(self):
        test_name = self.test_name_var.get().strip().replace(" ", "_") or "test"
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"{test_name}_playwright_automation_{date_str}.ts"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.generated_code.decode("utf-8") if isinstance(self.generated_code, bytes) else self.generated_code)

    def update_prompt(self):
        choice = self.source_type_var.get()
        self.prompt_text.delete("1.0", tk.END)
        if choice == "code":
            provided_text = (
                "You are provided the following:\n"
                "- Frontend and backend source code files for a web application"
            )
        elif choice == "analysis":
            provided_text = (
                "You are provided the following:\n"
                "- Design documents or functional specifications for a web application"
            )
        elif choice == "both":
            provided_text = (
                "You are provided the following:\n"
                "- Frontend and backend source code files for a web application\n"
                "- Design documents or functional specifications"
            )
                
        self.prompt_text.insert("1.0",
            f"You are a senior QA test engineer.\n\n"
            f"{provided_text}\n\n"
            "Your task:\n\n"
            "Based only on the available files, infer the business logic and user functionality of the application.\n"
            "- Represent realistic user behaviors and flows\n"
            "- Cover happy paths (successful actions)\n"
            "- Cover edge cases and error scenarios (invalid inputs, system limits, empty fields, etc.)\n"
            "- Include validation scenarios (required fields, format checks)\n"
            "- Are **independent and clearly described**\n"
            "- Are suitable for use in a UI test automation project\n\n"
            "Each scenario should include:\n"
            "1. A short title\n"
            "2. A one-line goal or description\n"
            "3. Steps the user would follow\n"
            "4. Expected results or validation points\n\n"
            "The output should be a numbered list of test scenarios."
        )

    def add_files(self):
        new_files = filedialog.askopenfilenames(title="Select Files", filetypes=[("All files", "*.*")])
        for f in new_files:
            if f not in self.uploaded_files:
                self.uploaded_files.append(f)
                self.file_listbox.insert(tk.END, f)

    def remove_selected_file(self):
        selected_indices = self.file_listbox.curselection()
        for i in reversed(selected_indices):
            self.uploaded_files.pop(i)
            self.file_listbox.delete(i)

    def toggle_controls(self, state):
        # 1. Tüm buton ve giriş alanlarını kapat/aç
        widgets = [
            self.generate_button,
            self.generate_automation_button,
            self.add_button,
            self.remove_button,
            self.test_name_entry,
            self.model_menu,
            self.automation_model_menu,
            self.prompt_text,
            self.automation_prompt,
            self.save_and_continue_button,
            self.save_code_button
        ]
        for widget in widgets:
            widget.config(state=state)

        # 2. Radiobutton'ları kapat/aç (source type seçimi)
        for child in self.tab1.winfo_children():
            if isinstance(child, ttk.Radiobutton):
                child.config(state=state)              
            
    def generate_scenarios(self):
        self.toggle_controls("disabled")
        #self.tab_control.tab(index, state='disabled')
        start_time = datetime.now().strftime("%H:%M")
        self.status_label.config(text=f"{start_time} ⏳ Generating test scenarios...")
        thread = threading.Thread(target=self.run_inference, args=(start_time,))
        thread.start()

    def run_inference(self, start_time):
        test_name = self.test_name_var.get().strip().replace(" ", "_") or "test"
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        model = self.model_var.get()
        #files = "\n".join(self.uploaded_files)
        
        file_contents = ""
        for filepath in self.uploaded_files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    file_contents += f"\n\n--- File: {os.path.basename(filepath)} ---\n"
                    file_contents += f.read()
            except Exception as e:
                file_contents += f"\n\n--- File: {os.path.basename(filepath)} (Error reading file: {e}) ---\n"

        try:
            input_text = f"{prompt}\n\nnSource Files:\n{file_contents}"
            result = subprocess.run(
                ["ollama", "run", model],
                    input=input_text.encode("utf-8"),
                capture_output=True
            )
            response = result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
        except Exception as e:
            response = f"Error while calling model: {str(e)}"

        self.response_area.after(0, lambda: self.show_ai_response(response, start_time))

    def show_ai_response(self, response, start_time):
        self.generated_response = response
        self.response_area.delete("1.0", tk.END)
        self.response_area.insert("1.0", response)

        end_time = datetime.now().strftime("%H:%M")
        self.status_label.config(text=f"{start_time} → {end_time} Test scenarios generated.")
        self.toggle_controls("normal")

    def save_and_continue(self):
        test_name = self.test_name_var.get().strip().replace(" ", "_") or "test"
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"{test_name}_test_scenarios_{date_str}.txt"
        edited_response = self.response_area.get("1.0", tk.END).strip()
        with open(filename, "w", encoding="utf-8") as f:
            f.write(edited_response)
        self.tab_control.select(self.tab3)

if __name__ == "__main__":
    root = tk.Tk()
    app = AITestApp(root)
    root.mainloop()

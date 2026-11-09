\# SmartDesk – AI-Powered Helpdesk \& Ticket Management System



SmartDesk is a Django-based helpdesk application that helps organizations manage support tickets efficiently using AI-powered ticket categorization, priority prediction, and workload-based agent assignment.



\## Features



\- User authentication and role-based access (Employee, Agent, Admin)

\- Create, view, and manage support tickets

\- AI-powered ticket category prediction using Machine Learning

\- Automatic ticket priority suggestions

\- Workload-based agent assignment

\- Ticket comments and activity history

\- Notifications and audit logs

\- Admin and agent dashboards

\- AI analytics dashboard with prediction override tracking



\## Technology Stack



\- \*\*Backend:\*\* Python, Django

\- \*\*Database:\*\* MySQL

\- \*\*Frontend:\*\* HTML, CSS, JavaScript

\- \*\*Machine Learning:\*\* Scikit-learn, Pandas

\- \*\*Model Storage:\*\* Joblib

\- \*\*Charts:\*\* Chart.js

\- \*\*Version Control:\*\* Git and GitHub



\## Project Structure



```text

smartdesk/

├── accounts/

├── tickets/

├── notifications/

├── analytics/

├── assignments/

├── audit/

├── comments/

├── ai\_engine/

├── config/

├── templates/

├── manage.py

└── requirements.txt

```



\## Run Locally



1\. Clone the repository:



&#x20;  ```bash

&#x20;  git clone https://github.com/emmu14/SmartDesk-AI-Helpdesk.git

&#x20;  ```



2\. Open the project folder:



&#x20;  ```bash

&#x20;  cd SmartDesk-AI-Helpdesk

&#x20;  ```



3\. Create and activate a virtual environment:



&#x20;  ```bash

&#x20;  python -m venv venv

&#x20;  ```



&#x20;  Windows PowerShell:



&#x20;  ```powershell

&#x20;  .\\venv\\Scripts\\Activate.ps1

&#x20;  ```



4\. Install dependencies:



&#x20;  ```bash

&#x20;  python -m pip install -r requirements.txt

&#x20;  ```



5\. Create a `.env` file in the project root and configure your environment variables:



&#x20;  ```env

&#x20;  SECRET\_KEY=your-django-secret-key

&#x20;  ```



6\. Configure your MySQL database in Django settings.



7\. Apply migrations:



&#x20;  ```bash

&#x20;  python manage.py migrate

&#x20;  ```



8\. Create an administrator:



&#x20;  ```bash

&#x20;  python manage.py createsuperuser

&#x20;  ```



9\. Start the development server:



&#x20;  ```bash

&#x20;  python manage.py runserver

&#x20;  ```



Visit `http://127.0.0.1:8000/`.



\## Run Tests



```bash

python manage.py test

```



\## AI Model Note



The ticket classification model is an experimental portfolio implementation trained on a small sample dataset. Its current evaluation results should not be treated as proof of production-level accuracy. More training data and broader evaluation are needed.



\## Project Status



Under development. Further improvements include expanded automated testing, production security configuration, deployment, and documentation.



\## Developer



\*\*Emmanuvel Christin\*\*



GitHub: https://github.com/emmu14


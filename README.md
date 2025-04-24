# Discount Campaign Management API

This Django-based API manages discount campaigns with support for cart and delivery discounts, campaign duration/budget limits, per-customer daily usage caps, and customer targeting.

---

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Setup & Installation](#setup--installation)
- [Project Structure](#project-structure)
- [Data Models](#data-models)
- [API Endpoints](#api-endpoints)
  - [Campaign CRUD Endpoints](#campaign-crud-endpoints)
  - [Available Discount Campaigns Endpoint](#available-discount-campaigns-endpoint)
- [Testing](#testing)
- [Postman Collection](#postman-collection)
- [Troubleshooting](#troubleshooting)
- [Security & Permissions](#security--permissions)
- [Performance & Monitoring](#performance--monitoring)
- [Deployment](#deployment)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

## Features

- **Discount Types:** Cart-wide or delivery-only discounts.
- **Time & Budget Constraints:** Campaigns expire by date or when budget is exhausted.
- **Daily Usage Limits:** Restrict number of discount uses per customer per day.
- **Customer Targeting:** Apply campaigns globally or to specific users.
- **CRUD Operations:** Create, read, update, and delete campaigns.
- **Filtering API:** Fetch only active, in-budget campaigns matching customer and type.

---

## Technology Stack

- **Language:** Python 3.x
- **Framework:** Django, Django REST Framework
- **Database:** SQLite (default), configurable to Postgres or MySQL
- **API Docs:** drf-yasg (Swagger/OpenAPI)
- **Testing:** Django Test Framework, DRF APIClient

---

## Setup & Installation

1. **Clone the repo**
   ```bash
   git clone <repo-url>
   cd campaign_manager
   ```

2. **Create & activate virtualenv**
   ```bash
   python -m venv env
   env/Scripts/activate   # (Windows: env\Scripts\activate)
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure settings**
   - In `campaign_manager/settings.py`, add `'rest_framework'`, and `'discount'` to `INSTALLED_APPS`.
   - Set timezone:
     ```python
     TIME_ZONE = 'Asia/Kolkata'
     USE_TZ = True
     ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start server**
   ```bash
   python manage.py runserver
   ```

---

## Project Structure

```
campaign_manager/
├── campaign_manager/      # Project settings
├── discount/              # Discount app
│   ├── migrations/        # DB migrations
│   ├── models.py          # Campaign & DiscountUsage models
│   ├── serializers.py     # DRF serializers
│   ├── views.py           # API views
│   ├── urls.py            # App URL routes
│   └── tests.py           # Unit & integration tests
└── manage.py              # Django CLI
```

---

## Data Models

### Campaign
- **Fields:**
  - `name`, `discount_type` (`cart`/`delivery`)
  - `discount_value` (decimal)
  - `start_date`, `end_date`
  - `total_budget`, `used_budget`
  - `daily_usage_limit`
  - `allowed_customers` (ManyToMany to User)

Methods:
- `is_active()`: checks date range and budget.

### DiscountUsage

- **Fields:**
  - `campaign` (FK)
  - `customer` (FK)
  - `used_on` (date)
  - `transaction_count`

Use to enforce daily usage limits and track history.

---

## API Endpoints

Base URL: `http://localhost:8000/api`

### Campaign CRUD Endpoints

1. **List & Create**: `GET/POST /api/campaigns/`

   - **POST Body**:
     ```json
     {
       "name": "Holiday Sale",
       "discount_type": "cart",
       "discount_value": "15.00",
       "start_date": "2025-12-01T00:00:00Z",
       "end_date": "2025-12-10T23:59:59Z",
       "total_budget": "200.00",
       "daily_usage_limit": 2,
       "allowed_customers_ids": [1,2]
     }
     ```
   - **Responses**: `201 Created` with created object;
     `400 Bad Request` on validation errors.

2. **Retrieve / Update / Delete**: `GET/PUT/DELETE /api/campaigns/{id}/`

   - **PUT Body**: same as POST.
   - **Responses**: `200 OK` on GET/PUT, `204 No Content` on DELETE.

### Available Discount Campaigns Endpoint

**GET** `/api/available-campaigns/?customer_id=<id>&discount_type=<cart|delivery>`

- **Filters applied**:
  1. Active between `start_date` and `end_date`
  2. `used_budget < total_budget`
  3. Optional `discount_type`
  4. Optional `customer_id` targeting (global or specific)

- **Response**: `200 OK` with array of campaign objects.

---

## Testing

Run unit & integration tests:
```bash
python manage.py test -v 2
```

Covered scenarios:
- Campaign creation, retrieval, update, deletion.
- Available-campaigns filtering for global and targeted users.
- Edge cases: expired/budget-exhausted campaigns.

---

## Postman Collection

Import `postman/DiscountCampaign.postman_collection.json` for ready-to-use requests:
- Create/List campaigns
- Retrieve/Update/Delete campaign
- Fetch available campaigns

---

## Troubleshooting

- **Empty available campaigns**: check campaign dates, budget, discount_type, and `allowed_customers_ids`.
- **Invalid PK errors**: ensure referenced users/campaigns exist in DB.

---

## Security & Permissions

- By default, endpoints are open. Add DRF auth (Token/JWT) and `IsAuthenticated`/custom permissions for production.

---

## Performance & Monitoring

- Index `start_date`, `end_date`, and M2M tables.
- Add logging or Sentry for error tracking.

---

## Deployment

1. **Dockerize**: Create `Dockerfile` + `docker-compose.yml` (Postgres + Django + Gunicorn).
2. **Reverse Proxy**: Nginx + Gunicorn.
3. **Envs**: manage secrets with env vars (`DEBUG=False`, `SECRET_KEY`, DB credentials).

---

## Future Enhancements

- Weekly/monthly usage caps.
- Campaign analytics dashboard.
- Admin actions to pause/resume campaigns.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.


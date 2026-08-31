import pytest
from app.models.event_model import EventModel
from app.models.funnel_model import FunnelModel
from app.services.funnel_service import FunnelService

def test_funnel_nonexistent_id():
    res = FunnelService.calculate_funnel_metrics(99999)
    assert res is None

def test_funnel_empty_steps():
    f = FunnelModel.create_funnel("Empty Funnel", "No steps", steps=[])
    res = FunnelService.calculate_funnel_metrics(f["id"])
    assert res["total_steps"] == 0
    assert res["overall_conversion_pct"] == 0.0
    assert res["steps_analysis"] == []

def test_funnel_single_step():
    f = FunnelModel.create_funnel("Single Step", steps=[{"step_name": "Step 1", "event_name": "visit"}])
    EventModel.create_event("visit", "s_1", "/")
    EventModel.create_event("visit", "s_2", "/")

    res = FunnelService.calculate_funnel_metrics(f["id"])
    assert res["initial_visitors"] == 2
    assert res["final_conversions"] == 2
    assert res["overall_conversion_pct"] == 100.0
    assert res["steps_analysis"][0]["step_conversion_pct"] == 100.0

def test_funnel_two_steps_100_pct_conversion():
    f = FunnelModel.create_funnel("2-Step Perfect", steps=[
        {"step_name": "Step 1", "event_name": "view"},
        {"step_name": "Step 2", "event_name": "buy"}
    ])
    EventModel.create_event("view", "sess_perf_1", "/")
    EventModel.create_event("buy", "sess_perf_1", "/checkout")
    EventModel.create_event("view", "sess_perf_2", "/")
    EventModel.create_event("buy", "sess_perf_2", "/checkout")

    res = FunnelService.calculate_funnel_metrics(f["id"])
    assert res["initial_visitors"] == 2
    assert res["final_conversions"] == 2
    assert res["overall_conversion_pct"] == 100.0

def test_funnel_two_steps_0_pct_conversion():
    f = FunnelModel.create_funnel("2-Step Zero", steps=[
        {"step_name": "Step 1", "event_name": "view"},
        {"step_name": "Step 2", "event_name": "buy"}
    ])
    EventModel.create_event("view", "sess_z_1", "/")
    EventModel.create_event("view", "sess_z_2", "/")

    res = FunnelService.calculate_funnel_metrics(f["id"])
    assert res["initial_visitors"] == 2
    assert res["final_conversions"] == 0
    assert res["overall_conversion_pct"] == 0.0
    assert res["steps_analysis"][1]["drop_off_count"] == 2
    assert res["steps_analysis"][1]["drop_off_pct"] == 100.0

def test_funnel_four_steps_gradual_dropoff():
    f = FunnelModel.create_funnel("4-Step Ecom", steps=[
        {"step_name": "Home", "event_name": "ecom_home"},
        {"step_name": "Product", "event_name": "ecom_prod"},
        {"step_name": "Cart", "event_name": "ecom_cart"},
        {"step_name": "Purchase", "event_name": "ecom_buy"}
    ])
    # 4 users at Home
    for i in range(4):
        EventModel.create_event("ecom_home", f"s_grad_{i}", "/")
    # 3 users at Product (75%)
    for i in range(3):
        EventModel.create_event("ecom_prod", f"s_grad_{i}", "/product")
    # 2 users at Cart (50% of initial, 66.67% of step 2)
    for i in range(2):
        EventModel.create_event("ecom_cart", f"s_grad_{i}", "/cart")
    # 1 user at Purchase (25% overall)
    EventModel.create_event("ecom_buy", "s_grad_0", "/buy")

    res = FunnelService.calculate_funnel_metrics(f["id"])
    assert res["initial_visitors"] == 4
    assert res["final_conversions"] == 1
    assert res["overall_conversion_pct"] == 25.0
    assert res["steps_analysis"][1]["visitors_reached"] == 3
    assert res["steps_analysis"][2]["visitors_reached"] == 2
    assert res["steps_analysis"][3]["visitors_reached"] == 1

def test_funnel_sessions_isolated():
    f = FunnelModel.create_funnel("Step Iso", steps=[
        {"step_name": "A", "event_name": "ev_a"},
        {"step_name": "B", "event_name": "ev_b"}
    ])
    # Session 1 did A only
    EventModel.create_event("ev_a", "iso_1", "/a")
    # Session 2 did B only (should not be counted in step 2 because they skipped step 1)
    EventModel.create_event("ev_b", "iso_2", "/b")

    res = FunnelService.calculate_funnel_metrics(f["id"])
    assert res["initial_visitors"] == 1
    assert res["final_conversions"] == 0

def test_funnel_date_range_filtering():
    f = FunnelModel.create_funnel("Date Funnel", steps=[
        {"step_name": "A", "event_name": "dt_a"},
        {"step_name": "B", "event_name": "dt_b"}
    ])
    # In range
    EventModel.create_event("dt_a", "dt_s_1", "/a", created_at="2026-08-15 10:00:00")
    EventModel.create_event("dt_b", "dt_s_1", "/b", created_at="2026-08-15 11:00:00")
    # Out of range
    EventModel.create_event("dt_a", "dt_s_2", "/a", created_at="2026-08-01 10:00:00")
    EventModel.create_event("dt_b", "dt_s_2", "/b", created_at="2026-08-01 11:00:00")

    res = FunnelService.calculate_funnel_metrics(f["id"], start_date="2026-08-10", end_date="2026-08-20")
    assert res["initial_visitors"] == 1
    assert res["final_conversions"] == 1

def test_funnel_model_get_all():
    f1 = FunnelModel.create_funnel("List Funnel 1", steps=[{"step_name": "S1", "event_name": "E1"}])
    f2 = FunnelModel.create_funnel("List Funnel 2", steps=[{"step_name": "S2", "event_name": "E2"}])
    all_f = FunnelModel.get_all()
    assert len(all_f) >= 2
    ids = [f["id"] for f in all_f]
    assert f1["id"] in ids
    assert f2["id"] in ids

def test_funnel_zero_initial_visitors():
    f = FunnelModel.create_funnel("No Visitors", steps=[{"step_name": "S1", "event_name": "unheard_event"}])
    res = FunnelService.calculate_funnel_metrics(f["id"])
    assert res["initial_visitors"] == 0
    assert res["final_conversions"] == 0
    assert res["overall_conversion_pct"] == 0.0

def test_funnel_duplicate_events_in_same_session():
    f = FunnelModel.create_funnel("Dedup Session", steps=[
        {"step_name": "View", "event_name": "view_dup"},
        {"step_name": "Click", "event_name": "click_dup"}
    ])
    # User views 3 times, clicks 2 times
    EventModel.create_event("view_dup", "dup_sess", "/")
    EventModel.create_event("view_dup", "dup_sess", "/")
    EventModel.create_event("view_dup", "dup_sess", "/")
    EventModel.create_event("click_dup", "dup_sess", "/click")
    EventModel.create_event("click_dup", "dup_sess", "/click")

    res = FunnelService.calculate_funnel_metrics(f["id"])
    assert res["initial_visitors"] == 1
    assert res["final_conversions"] == 1
    assert res["overall_conversion_pct"] == 100.0

def test_funnel_dropoff_calculation_precision():
    f = FunnelModel.create_funnel("Precision Funnel", steps=[
        {"step_name": "A", "event_name": "prec_a"},
        {"step_name": "B", "event_name": "prec_b"}
    ])
    # 3 users do A, 1 does B -> 33.33% conversion, 66.67% dropoff
    EventModel.create_event("prec_a", "p_1", "/")
    EventModel.create_event("prec_a", "p_2", "/")
    EventModel.create_event("prec_a", "p_3", "/")
    EventModel.create_event("prec_b", "p_1", "/b")

    res = FunnelService.calculate_funnel_metrics(f["id"])
    assert res["steps_analysis"][1]["step_conversion_pct"] == 33.33
    assert res["steps_analysis"][1]["drop_off_pct"] == 66.67

def test_funnel_step_order_preservation():
    f = FunnelModel.create_funnel("Order Funnel", steps=[
        {"step_name": "First", "event_name": "st_1"},
        {"step_name": "Second", "event_name": "st_2"},
        {"step_name": "Third", "event_name": "st_3"}
    ])
    fetched = FunnelModel.get_by_id(f["id"])
    steps = fetched["steps"]
    assert steps[0]["step_order"] == 1
    assert steps[1]["step_order"] == 2
    assert steps[2]["step_order"] == 3

def test_funnel_description_optional():
    f = FunnelModel.create_funnel("No Desc Funnel")
    assert f["description"] is None

def test_funnel_total_steps_metric():
    f = FunnelModel.create_funnel("Three Steps", steps=[
        {"step_name": "A", "event_name": "a"},
        {"step_name": "B", "event_name": "b"},
        {"step_name": "C", "event_name": "c"}
    ])
    res = FunnelService.calculate_funnel_metrics(f["id"])
    assert res["total_steps"] == 3

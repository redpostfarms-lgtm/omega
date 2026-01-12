@echo off
cls
echo ================================================================================
echo OMEGA DEVELOPER INTEGRATIONS - STATUS
echo ================================================================================
echo.
python -c "from omega_developer_integrations import get_integration_manager; m = get_integration_manager(); r = m.get_setup_report(); print('Total Tools:', r['total_tools']); print('Complete:', r['complete']); print('Needs Setup:', r['needs_setup']); print('Needs Human:', r['needs_human']); print(); print('Tools:'); [print(f\"  - {info['name']}: {info['status']}\") for info in r['tools'].values()]"
echo.
echo ================================================================================
echo To set up tools, run: python SETUP_DEVELOPER_INTEGRATIONS.py
echo ================================================================================
pause

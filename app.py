
➕ Ajouter un élève
Nom de l'élève

Niveau de départ



FAVEDS 🤸



Stratégie 🧠



Coopération 🤝



📊 Suivi Général des Élèves
Modifiez directement les valeurs dans le tableau ci-dessous.

🔍 Sélectionner un élève
Choisir un élève
Jérome

📌 Fiche de Jérome
Niveau : 300.0

Points de Compétence : 20.0

🛒 Boutique des Pouvoirs
🛍️ Choisir un pouvoir
Roi / Reine de la séquence

numpy._core._exceptions._UFuncNoLoopError: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).
Traceback:
File "/mount/src/streamlit-suvi-eps-/app.py", line 93, in <module>
    st.session_state["students"].loc[st.session_state["students"]["Nom"] == selected_student, "Pouvoirs"] += f", {selected_item}" if student_data["Pouvoirs"] else selected_item
File "/home/adminuser/venv/lib/python3.12/site-packages/pandas/core/generic.py", line 12719, in __iadd__
    return self._inplace_method(other, type(self).__add__)  # type: ignore[operator]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.12/site-packages/pandas/core/generic.py", line 12689, in _inplace_method
    result = op(self, other)
             ^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.12/site-packages/pandas/core/ops/common.py", line 76, in new_method
    return method(self, other)
           ^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.12/site-packages/pandas/core/arraylike.py", line 186, in __add__
    return self._arith_method(other, operator.add)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.12/site-packages/pandas/core/series.py", line 6135, in _arith_method
    return base.IndexOpsMixin._arith_method(self, other, op)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.12/site-packages/pandas/core/base.py", line 1382, in _arith_method
    result = ops.arithmetic_op(lvalues, rvalues, op)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.12/site-packages/pandas/core/ops/array_ops.py", line 283, in arithmetic_op
    res_values = _na_arithmetic_op(left, right, op)  # type: ignore[arg-type]
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.12/site-packages/pandas/core/ops/array_ops.py", line 218, in _na_arithmetic_op
    result = func(left, right)
             ^^^^^^^^^^^^^^^^^

# Variables and controls

Independent variable: strategy (`single`, `majority`, `debate`). Evidence-enabled debate is an additional future condition, not a currently contracted benchmark strategy.

Dependent variables: exact-match accuracy, Brier score, ECE, latency, available token usage, failure rate. Citation support, unsupported claim rate, abstention coverage and money cost require separately documented annotation/accounting if not exported by the implementation.

Control question wording/order, dataset version, model mapping, prompt versions, answer extraction, supported sampling parameters, evidence corpus/access, repetitions and machine environment. Different information access confounds the isolated effect of debate. Different call counts are part of the strategy cost and must be disclosed.

Same-model agents are separate calls with correlated errors, not independent knowledge sources. Provider fields absent from responses are missing, not zero.

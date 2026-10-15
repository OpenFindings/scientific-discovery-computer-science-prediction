# Zero Extension: an exact boundary-signature lemma on trees

Task: `THEORY-ZEROEXT-BOUNDARY-SIGNATURE-001`
Candidate: `ZERO-EXTENSION-EXACT-SPARSIFIER-005`
Audit date: 2026-10-15

This note contains the mathematical proof and source-scope audit. The Supervisor
also attempted one bounded theory-worker execution: the worker produced the
structured JSON and this exposition, but the execution was rejected at the
workflow layer because it also tried to modify `scripts/research_supervisor.py`.
That write conflict is preserved in `research/supervisor_events.jsonl`; no
experiment or experiment-budget renewal occurred, and Paper 3 was not changed.

## 1. Source definition and quantifiers

The source-matched target is Reidl--Wahlström, *Parameterized Algorithms for Zero
Extension and Metric Labelling Problems* (2018), arXiv:1802.06026v1. The local
source/theorem audit is `reports/zero_extension_theorem_and_novelty_audit_20261015.md`.
The source instance notation includes a threshold \(q\), but the exact metric
sparsifier condition is equality of the restricted optimum below; \(q\) is relevant
to the source's kernel consequence and is not needed for this equality lemma.

Let \(G=(V,E)\) be a finite graph with terminal set \(S\), let \(D\) be a finite
label set with \(|D|\le s\), let \(\mu\) be a metric on \(D\), and let
\(\tau:S\to D\) be injective. A \(\tau\)-extension is a map
\(\lambda:V\to D\) with \(\lambda|_S=\tau\). Its cost and crossing number are

\[
 \operatorname{cost}_G(\lambda)=\sum_{uv\in E}\mu(\lambda(u),\lambda(v)),
 \qquad
 \operatorname{cr}_G(\lambda)=|\{uv\in E:\lambda(u)\ne\lambda(v)\}|.
\]

Define

\[
 \operatorname{OPT}_{G,k}(\mu,\tau)=
 \min\{\operatorname{cost}_G(\lambda):
       \lambda|_S=\tau,\ \operatorname{cr}_G(\lambda)\le k\},
\]

with value \(+\infty\) if the feasible set is empty. An exact \(k\)-bounded metric
sparsifier must preserve this value for every admissible \(D,\mu,\tau\), not merely
terminal cuts, multicommodity flows, approximate costs, or one fixed labeling.

The phrase “exponent independent of \(s\)” needs care. A bound
\(O(k^c)\) with no label-count factor is impossible as a literal statement for
arbitrarily many terminals, because the output must retain the terminals. The
relevant form here is \(f(s)k^c\), with universal \(c\) and an explicit permitted
factor \(f(s)\). The source's general-graph construction gives \(O(k^{s+1})\) for
fixed \(s\); its proof uses \(s\) gammoid layers plus one uniform layer. That source
fact is prior art, not a lower bound.

## 2. Label-independent boundary signature

For a tree \(T\), first delete terminal-free leaves repeatedly. Then, in the
minimal subtree connecting \(S\), suppress every maximal path whose internal
vertices are nonterminals of degree two. Let \(C=C(T,S)\) be the resulting
terminal core. The construction depends only on \(T\) and \(S\), not on \(D,\mu,\tau\),
or \(k\).

For each suppressed path \(P\) with endpoints \(x,y\), use the boundary signature

\[
 \sigma_P(a,b)=\bigl(\mu(a,b),\mathbf 1[a\ne b]\bigr),
 \qquad (a,b)\in D^2.
\]

The signature schema is label-independent: it stores only the two boundary ports
and the two quantities needed by the objective, and the core itself does not change
when the label universe or metric changes. It is not claiming that the numerical
value \(\mu(a,b)\) is independent of labels. This distinction prevents hidden
\(s\)-dependence from being smuggled into the graph construction.

## 3. Exact two-sided lemma

**Lemma (tree-core preservation).** For every finite connected unweighted tree
\(T\), terminal set \(S\), integer \(k\ge0\), finite metric \((D,\mu)\) with
\(|D|\le s\), and injective \(\tau:S\to D\),

\[
 \operatorname{OPT}_{T,k}(\mu,\tau)
 =
 \operatorname{OPT}_{C(T,S),k}(\mu,\tau).
\]

The core has the same terminals and, for \(|S|=m\ge2\), at most \(2m-3\) edges.
Thus the restricted tree class has an exact sparsifier of size
\(O(s)\,k^0\): the \(k\)-exponent is \(0\), while the terminal-count factor is
explicit. This is a restricted theorem, not a uniform \(O(1)\)-size claim.

### Proof: terminal-free leaves

Let \(x\) be a deleted nonterminal leaf with parent \(y\). Given any labeling of
the remaining tree, set \(\lambda(x)=\lambda(y)\). The deleted edge then contributes
zero cost and zero crossings. Conversely, restricting a labeling of the larger tree
removes a nonnegative cost and a nonnegative number of crossings. The optimum under
an upper crossing bound is therefore unchanged. Iterate this operation.

### Proof: one suppressed path, original to core

Let \(P=x_0x_1\ldots x_\ell\) be a suppressed path and let endpoint labels be
\(a=\lambda(x_0)\), \(b=\lambda(x_\ell)\). For any labels \(z_i=\lambda(x_i)\),
the metric triangle inequality gives

\[
 \sum_{i=1}^{\ell}\mu(z_{i-1},z_i)\ge\mu(a,b).
\]

If \(a=b\), the replacement edge has zero cost and zero crossings. If \(a\ne b\),
the path has at least one crossing, whereas the replacement edge has exactly one.
Consequently replacing every such path by its core edge maps every feasible tree
labeling to a core labeling with no greater cost and no greater crossing number.
Hence \(\operatorname{OPT}_{C,k}\le\operatorname{OPT}_{T,k}\).

### Proof: core to original

Given a core labeling, on each suppressed path with endpoint labels \(a,b\), label
all internal vertices by \(a\). The path then has cost \(\mu(a,b)\), exactly the
replacement-edge cost. It has zero crossings if \(a=b\), and exactly one crossing
if \(a\ne b\), exactly matching the signature's disagreement bit. Give every
deleted leaf its parent's label. The resulting tree labeling has identical cost
and crossing number, so \(\operatorname{OPT}_{T,k}\le\operatorname{OPT}_{C,k}\).

The two inequalities prove equality. They also cover the \(+\infty\) case: a
feasible labeling on either side would map to a feasible labeling on the other.

### Proof: size

For \(m\ge2\), every leaf of \(C\) is terminal and every nonterminal has degree at
least three. If \(b\) is the number of nonterminal vertices, the tree degree
identity gives \(b\le m-2\). Therefore

\[
 |E(C)|=|V(C)|-1=m+b-1\le2m-3.
\]

For \(m=0\), use the empty graph; for \(m=1\), use one isolated terminal. Both
cases preserve the value (zero whenever feasible).

## 4. Adversarial checks and limits

The proof uses only nonnegativity, the triangle inequality, and the fact that every
tree edge has unit weight. It remains valid for \(k=0\), repeated nonterminal
labels, zero distances in a pseudometric if those are admitted by the source, and
the one- and two-terminal boundary cases. It does not use the number of labels in
the construction or in either inequality. The only explicit label-count dependence
is the unavoidable \(O(|S|)\le O(s)\) output-size factor.

Weighted trees are outside this lemma: replacing a path by one unweighted edge
does not preserve weighted cost, and a weighted replacement would require a
separate crossing/cost proof. General graphs are outside it for the same reason
that path replacements can interact through cycles and multiple routes.

Cacti are also not discharged. A cycle can provide two or more boundary routes;
changing one route's labels can alter both the cost and the global crossing budget,
so the independent path-signature composition above is unavailable. This is an
unresolved proof obligation, not a counterexample: no source-matched cactus
obstruction was established in this audit.

The source audit also rules out two invalid shortcuts. Exact flow/cut or
Steiner-node results do not transfer without a reduction preserving this exact
metric-labeling objective and crossing restriction. The final version of
Wahlström's multicut work retracts its preliminary 0-Extension sparsifier claim;
its unsupported sparse-cut step must not be reused as a proof or lower bound.

No finite enumeration was run. In particular, this lemma is not an asymptotic
lower bound, and no finite observation is promoted into one. The contraction-only
lower-bound obligation is not needed after the tree lemma; it remains open for the
unrestricted sparsifier model and is not inferred here.

## 5. Result classification and next falsifiable action

Discharged: the narrowest nontrivial two-sided obligation on unweighted trees.
The result establishes a label-independent *construction* and a universal
\(k\)-exponent \(0\) for that restricted class, with explicit \(O(s)\) terminal
factor. It does not resolve the source's unrestricted exact metric-sparsifier
question, prove anything for weighted trees or cacti, or validate a contraction-only
lower bound.

Next falsifiable action: attempt a cactus lemma by isolating a single cycle and
writing a complete two-sided boundary signature. If the cycle signature cannot be
closed under both cost and crossing-budget composition, record the smallest
source-matched obstruction and then reassess the contraction-only obligation O7;
do not treat that obstruction as an asymptotic lower bound without a separate
quantified construction.

Paper 3 Target A and Target B remain unchanged.

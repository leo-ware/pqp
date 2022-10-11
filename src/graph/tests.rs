#![cfg(test)]

// use super::{GraphBuilder, Set};

// #[test]
// fn test_graph_builder () {
//     let mut gb = GraphBuilder::new();
//     let a = "a";
//     let b = "b";
//     let c = "c";
//     let d = "d";

//     gb.add_edge(a, b);
//     assert!(gb.get_nodes().contains(a));
//     assert!(!gb.get_nodes().contains(c));

//     gb.add_node(c);
//     assert!(gb.get_nodes().contains(c));
//     assert!(!gb.get_nodes().contains(d));
//     assert!(gb.get_edges().contains_key(a));
//     assert!(gb.get_edges()[a] == Set::from([b]));
// }

// #[test]
// fn test_to_digraph () {
//     let mut gb = GraphBuilder::new();
//     let a = "a";
//     let b = "b";
//     let c = "c";

//     gb.add_edge(a, b);
//     gb.add_node(c);
//     let dg = GraphBuilder::to_digraph(gb);

//     assert!(dg.root_set() == vec![a, c] || dg.root_set() == vec![c, a]);
//     assert_eq!(dg.ancestors(a), Set::from([b]));
//     assert_eq!(dg.order().last(), Some(&b));
//     assert_eq!(dg.order().len(), 3);
//     assert_eq!(dg.count_parents()[b], 1);
//     assert_eq!(dg.count_parents()[a], 0);
//     assert_eq!(dg.count_parents()[c], 0);
// }

// #[test]
// fn test_to_bigraph () {
//     let mut gb = GraphBuilder::new();
//     let a = "a";
//     let b = "b";
//     let c = "c";

//     gb.add_edge(a, b);
//     gb.add_node(c);
//     let bg = GraphBuilder::to_bigraph(gb);

//     assert!(bg.c_components() == vec![Set::from([a, b]), Set::from([c])] ||
//             bg.c_components() == vec![Set::from([c]), Set::from([a, b])],
//             "Failed because: bg.c_components() == {:#?}", bg.c_components())
// }